"""
Surfcam prototype - closed-loop tracking. Combines the UDP video receiver
(webcam_track_network_udp.py) with the UDP servo sender
(servo_control_test.py): target pixel offset from frame center drives
pan/tilt corrections automatically, sent to pi/servo_udp_receiver.py.

Control scheme: critically damped spring-follow per axis, not raw
per-frame position steps.
  - DEADBAND_PX: pixel error below this threshold is treated as zero, so
    detection noise doesn't give the spring anything to chase.
  - Each axis's spring target is `current_angle + FOV-derived deg/pixel *
    error` - a moving goalpost re-aimed every frame from the newest
    detection, not a fixed setpoint.
  - The spring's resulting velocity is capped every frame via
    speed_curve.TuningConfig: a live-editable curve (see the second
    OpenCV window) maps how far off-center the target is to a fraction of
    that axis's max speed. The spring supplies the smooth
    acceleration/deceleration; the curve only ever clips the outcome.
  - Runs even with no target detected, decelerating toward zero rather
    than holding whatever velocity it had when the target was lost.

Tuning (omega_n, zeta, per-axis max speed, the curve itself) lives in
prototype/tracking_tuning.json, editable live via the curve window.

Auto-tracking starts OFF; press 'a' to enable so servos don't move the
instant this script launches.

Usage:
    python tracking_servo_control.py <pi-ip> [video_port] [servo_port]
    # video_port defaults to 5005 (must match stream_webcam_udp.py)
    # servo_port defaults to 6000 (must match servo_udp_receiver.py)

Controls:
    a - toggle auto-tracking on/off
    q - quit
"""

import math
import socket
import struct
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from speed_curve import CurveEditor, TuningConfig

# "face" for indoor testing, "person" for outdoor tracking.
TARGET_MODE = "person"

MODELS_DIR = Path(__file__).resolve().parent / "models"

if TARGET_MODE == "face":
    MODEL_NAME = str(MODELS_DIR / "face_yolov8n.pt")
    TRACK_CLASSES = None  # face model is already single-class
else:
    MODEL_NAME = str(MODELS_DIR / "yolo26n.pt")
    TRACK_CLASSES = [0]  # COCO person class

DEFAULT_VIDEO_PORT = 5005
DEFAULT_SERVO_PORT = 6000
RECV_BUFFER_SIZE = 65536

PAN = "pan"
TILT = "tilt"

# Mirrors pi/servo_udp_receiver.py's SAFE_RANGE, enforced here too so the
# commanded angle never exceeds what the Pi will clamp to. Positive tilt
# = down, negative = up.
SAFE_RANGE = {
    PAN: (-80, 80),
    TILT: (-40, 10),
}

# Matches pi/servo_udp_receiver.py's DEFAULT_ANGLE - camera roughly level.
DEFAULT_ANGLE = {
    PAN: 0.0,
    TILT: -30.0,
}

PACKET_FORMAT_OUT = struct.Struct(">ff")  # pan_angle, tilt_angle sent to the Pi

DEADBAND_PX = 20

# Logitech C270 spec is 55 degrees diagonal FOV on current-revision units
# (older units spec 60 - unconfirmed which this camera actually is). Split
# across the 16:9 frame via the standard diagonal/aspect-ratio relation to
# get real per-axis degrees-per-pixel, replacing a hand-tuned gain. This
# assumes a rectilinear lens; real lenses have some barrel distortion, so
# edge pixels correspond to slightly more real-world angle than a linear
# split implies. Re-derive from an empirical measurement if corrections
# consistently over/undershoot.
CAMERA_DIAGONAL_FOV_DEG = 55.0


def _split_fov(diagonal_deg, aspect_w, aspect_h):
    diag_units = math.hypot(aspect_w, aspect_h)
    half_diag_rad = math.radians(diagonal_deg / 2)
    h_fov = 2 * math.degrees(math.atan((aspect_w / diag_units) * math.tan(half_diag_rad)))
    v_fov = 2 * math.degrees(math.atan((aspect_h / diag_units) * math.tan(half_diag_rad)))
    return h_fov, v_fov


HORIZONTAL_FOV_DEG, VERTICAL_FOV_DEG = _split_fov(CAMERA_DIAGONAL_FOV_DEG, 16, 9)

# Pan/Tilt polarity correction
PAN_SIGN = -1
TILT_SIGN = 1

TUNING_CONFIG_PATH = Path(__file__).resolve().parent / "tracking_tuning.json"

latest_frame = None
frame_lock = threading.Lock()
frame_ready = threading.Event()
running = True

# Set once in main() and unchanged afterward - safe to read from a global
# rather than threading them through every send_servo_command() call.
servo_sock = None
pi_ip = None
servo_port = None


def receive_loop(sock):
    global latest_frame
    while running:
        try:
            data, _ = sock.recvfrom(RECV_BUFFER_SIZE)
        except OSError:
            break
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            continue
        with frame_lock:
            latest_frame = frame
        frame_ready.set()


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def send_servo_command(pan_angle, tilt_angle):
    data = PACKET_FORMAT_OUT.pack(pan_angle, tilt_angle)
    servo_sock.sendto(data, (pi_ip, servo_port))


def spring_step(angle, velocity, target_angle, omega_n, zeta, velocity_cap, dt):
    """One critically-damped (when zeta=1) spring-follow update. Returns
    the new (angle, velocity). velocity_cap clips the spring's own output
    rather than driving the motion itself - see module docstring."""
    acceleration = omega_n ** 2 * (target_angle - angle) - 2 * zeta * omega_n * velocity
    velocity = clamp(velocity + acceleration * dt, -velocity_cap, velocity_cap)
    angle += velocity * dt
    return angle, velocity


def main():
    global running, servo_sock, pi_ip, servo_port

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python tracking_servo_control.py <pi-ip> [video_port] [servo_port]")

    pi_ip = sys.argv[1]
    video_port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_VIDEO_PORT
    servo_port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SERVO_PORT

    model = YOLO(MODEL_NAME)

    video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    video_sock.bind(("0.0.0.0", video_port))
    print(f"Listening for video on port {video_port}")

    servo_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    receiver = threading.Thread(target=receive_loop, args=(video_sock,), daemon=True)
    receiver.start()

    tuning = TuningConfig.load(TUNING_CONFIG_PATH)
    editor = CurveEditor(tuning, TUNING_CONFIG_PATH)

    # set initial safe angles for the camera to look roughly straight ahead
    pan_angle = DEFAULT_ANGLE[PAN]
    tilt_angle = DEFAULT_ANGLE[TILT]
    pan_velocity = 0.0
    tilt_velocity = 0.0

    send_servo_command(pan_angle, tilt_angle)
    auto_tracking = False
    print("Auto-tracking is OFF. Press 'a' to enable, 'q' to quit.")

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            got_new = frame_ready.wait(timeout=0.5)
            key = cv2.waitKey(1) & 0xFF  # checking for q or a input, also pumps the curve editor window
            if key == ord("q"):
                break
            if key == ord("a"):
                auto_tracking = not auto_tracking
                print(f"Auto-tracking: {'ON' if auto_tracking else 'OFF'}")

            if not got_new:
                continue
            frame_ready.clear()

            # Image Processing
            with frame_lock:
                frame = latest_frame.copy() if latest_frame is not None else None
            if frame is None:
                continue

            now = time.time()
            dt = min(now - prev_time, 0.2)  # cap dt so a stall/breakpoint can't fling the spring

            h, w = frame.shape[:2]
            frame_cx, frame_cy = w // 2, h // 2

            results = model.track(
                frame,
                classes=TRACK_CLASSES,
                persist=True,
                verbose=False,
            )
            result = results[0]

            # Pick the target: largest bounding box (closest / most prominent person/face/etc)
            target_box = None
            target_id = None
            target_conf = None
            best_area = 0
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    area = (x2 - x1) * (y2 - y1)
                    if area > best_area:
                        best_area = area
                        target_box = (int(x1), int(y1), int(x2), int(y2))
                        target_id = int(box.id[0]) if box.id is not None else None
                        target_conf = float(box.conf[0])

            # Draw all detections faintly, largest target in bright green, all others in grey
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    is_target = (x1, y1, x2, y2) == target_box
                    color = (0, 255, 0) if is_target else (100, 100, 100)
                    thickness = 2 if is_target else 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            cv2.drawMarker(frame, (frame_cx, frame_cy), (0, 0, 255),
                            markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

            # err_x/err_y stay (0, 0) with no target, so the spring below
            # decelerates toward its current angle instead of holding
            # whatever velocity it had when the target was lost.
            err_x, err_y = 0, 0
            if target_box is not None:
                x1, y1, x2, y2 = target_box
                target_cx, target_cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(frame, (target_cx, target_cy), 6, (0, 255, 0), -1)
                cv2.line(frame, (frame_cx, frame_cy), (target_cx, target_cy), (0, 255, 255), 2)

                err_x = target_cx - frame_cx
                err_y = target_cy - frame_cy
                label = f"id={target_id} conf={target_conf * 100:.0f}% err=({err_x:+d},{err_y:+d})"
                cv2.putText(frame, label, (x1, max(20, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "no target", (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if auto_tracking:
                eff_err_x = err_x if abs(err_x) > DEADBAND_PX else 0
                eff_err_y = err_y if abs(err_y) > DEADBAND_PX else 0

                deg_per_pixel_pan = HORIZONTAL_FOV_DEG / w
                deg_per_pixel_tilt = VERTICAL_FOV_DEG / h
                pan_target = pan_angle + PAN_SIGN * deg_per_pixel_pan * eff_err_x
                tilt_target = tilt_angle + TILT_SIGN * deg_per_pixel_tilt * eff_err_y

                pan_frac = min(abs(eff_err_x) / frame_cx, 1.0)
                tilt_frac = min(abs(eff_err_y) / frame_cy, 1.0)
                pan_cap = tuning.curve.value(pan_frac) * tuning.pan_max_speed_deg_s
                tilt_cap = tuning.curve.value(tilt_frac) * tuning.tilt_max_speed_deg_s

                pan_angle, pan_velocity = spring_step(
                    pan_angle, pan_velocity, pan_target, tuning.omega_n, tuning.zeta, pan_cap, dt)
                tilt_angle, tilt_velocity = spring_step(
                    tilt_angle, tilt_velocity, tilt_target, tuning.omega_n, tuning.zeta, tilt_cap, dt)

                pan_lo, pan_hi = SAFE_RANGE[PAN]
                tilt_lo, tilt_hi = SAFE_RANGE[TILT]
                pan_angle = clamp(pan_angle, pan_lo, pan_hi)
                tilt_angle = clamp(tilt_angle, tilt_lo, tilt_hi)

                send_servo_command(pan_angle, tilt_angle)
                editor.live_marker_x = max(pan_frac, tilt_frac)
            else:
                editor.live_marker_x = None

            fps = 0.9 * fps + 0.1 * (1.0 / max(dt, 1e-6))
            prev_time = now
            status = "ON" if auto_tracking else "OFF"
            cv2.putText(frame, f"FPS: {fps:.1f}  auto-tracking: {status}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"pan={pan_angle:.1f} ({pan_velocity:+.1f} deg/s)  "
                                f"tilt={tilt_angle:.1f} ({tilt_velocity:+.1f} deg/s)", (20, 690),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

            cv2.imshow("Surfcam prototype - closed-loop tracking", frame)
            editor.render()
    finally:
        running = False
        video_sock.close()
        servo_sock.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
