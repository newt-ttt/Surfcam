"""
Surfcam prototype - closed-loop tracking with the camera captured locally
(no UDP video stream). Same YOLO tracking / spring-follow / hand-tuned
speed-curve control as tracking_servo_control.py, but the webcam plugs
straight into whatever machine runs this script (see webcam_track.py's
capture setup) instead of receiving frames from stream_webcam_udp.py on
the Pi. Only servo angle commands go over the network, to
pi/servo_udp_receiver.py - meant for testing whether skipping the video
network hop is worth it on weaker hardware (e.g. a laptop) vs. the
processing-time cost of running YOLO on that hardware instead of the
desktop's GPU.

Shares prototype/tracking_tuning.json with tracking_servo_control.py, so
curve/spring tuning stays consistent between the two.

Usage:
    python mobile_tracking_servo_control.py <pi-ip> [servo_port]
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
from pygrabber.dshow_graph import FilterGraph
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from speed_curve import CurveEditor, TuningConfig

# "face" for indoor testing, "person" for outdoor tracking.
TARGET_MODE = "person"

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

if TARGET_MODE == "face":
    MODEL_NAME = str(MODELS_DIR / "face_yolov8n.pt")
    TRACK_CLASSES = None  # face model is already single-class
else:
    MODEL_NAME = str(MODELS_DIR / "yolo26n.pt")
    TRACK_CLASSES = [0]  # COCO person class

CAMERA_NAME_HINT = "C270"
FALLBACK_CAMERA_INDEX = 0  # laptop's built-in webcam, if no C270 is found

# Show the live-draggable speed-curve editor window. Off by default - the JSON
# tuning is used as-is; set True to visually tune the curve (edits persist to
# tracking_tuning.json). Disabling it also drops a second imshow per frame.
SHOW_CURVE_UI = False

DEFAULT_SERVO_PORT = 6000

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

# See tracking_servo_control.py's module docstring for the FOV-split
# rationale - same camera, same math.
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

TUNING_CONFIG_PATH = Path(__file__).resolve().parent.parent / "tracking_tuning.json"

# BoT-SORT with global motion compensation disabled - GMC's sparseOptFlow
# was ~37 ms/frame of overhead (over 2x the whole tracker cost) and its
# benefit is marginal here since we just pick the largest box each frame.
TRACKER_CONFIG = str(Path(__file__).resolve().parent.parent / "botsort_nogmc.yaml")

latest_frame = None
frame_lock = threading.Lock()
frame_ready = threading.Event()
running = True


def capture_loop(cap):
    """Runs cap.read() on a background thread so camera I/O wait overlaps
    with model.track() instead of serializing - mirrors
    tracking_servo_control.py's receive_loop/frame_lock/frame_ready
    pattern, just fed by cap.read() instead of a UDP socket."""
    global latest_frame
    while running:
        ok, frame = cap.read()
        if not ok:
            break
        with frame_lock:
            latest_frame = frame
        frame_ready.set()


def find_camera_index(name_hint: str):
    """Resolve a device index by (partial, case-insensitive) name via DirectShow
    enumeration. Falls back to FALLBACK_CAMERA_INDEX (the machine's default/
    built-in webcam) if no match is found, since this script is meant to run
    on whatever hardware is being tested, not just a machine with a C270
    plugged in."""
    devices = FilterGraph().get_input_devices()
    for i, name in enumerate(devices):
        if name_hint.lower() in name.lower():
            return i
    print(f"No camera matching '{name_hint}' found (devices: {devices}); "
          f"falling back to index {FALLBACK_CAMERA_INDEX}")
    return FALLBACK_CAMERA_INDEX


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def send_servo_command(servo_sock, pi_ip, servo_port, pan_angle, tilt_angle):
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
    global running

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python mobile_tracking_servo_control.py <pi-ip> [servo_port]")

    pi_ip = sys.argv[1]
    servo_port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SERVO_PORT

    model = YOLO(MODEL_NAME)

    camera_index = find_camera_index(CAMERA_NAME_HINT)
    print(f"Using camera index {camera_index}")

    # CAP_MSMF instead of CAP_DSHOW: see webcam_track.py - DSHOW gets stuck
    # in slow YUY2 mode on the C270, MSMF negotiates MJPG correctly.
    cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {camera_index}")

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Let auto-exposure/auto-white-balance settle.
    for _ in range(15):
        cap.read()

    capturer = threading.Thread(target=capture_loop, args=(cap,), daemon=True)
    capturer.start()

    servo_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    tuning = TuningConfig.load(TUNING_CONFIG_PATH)
    editor = CurveEditor(tuning, TUNING_CONFIG_PATH) if SHOW_CURVE_UI else None

    pan_angle = DEFAULT_ANGLE[PAN]
    tilt_angle = DEFAULT_ANGLE[TILT]
    pan_velocity = 0.0
    tilt_velocity = 0.0

    send_servo_command(servo_sock, pi_ip, servo_port, pan_angle, tilt_angle)
    auto_tracking = False
    print("Auto-tracking is OFF. Press 'a' to enable, 'q' to quit.")

    prev_time = time.perf_counter()  # perf_counter: monotonic, sub-us - time.time()'s
    fps = 0.0                        # ~15ms Windows resolution let dt round to 0 (=> 1e6 fps spike)
    first_frame = True               # first interval is only startup, not a real frame - skip it

    try:
        while True:
            got_new = frame_ready.wait(timeout=0.5)
            key = cv2.waitKey(1) & 0xFF  # checking for q or a input
            if key == ord("q"):
                break
            if key == ord("a"):
                auto_tracking = not auto_tracking
                print(f"Auto-tracking: {'ON' if auto_tracking else 'OFF'}")

            if not got_new:
                continue
            frame_ready.clear()

            with frame_lock:
                frame = latest_frame.copy() if latest_frame is not None else None
            if frame is None:
                continue

            now = time.perf_counter()
            dt = min(now - prev_time, 0.2)  # cap dt so a stall/breakpoint can't fling the spring

            h, w = frame.shape[:2]
            frame_cx, frame_cy = w // 2, h // 2

            results = model.track(
                frame,
                classes=TRACK_CLASSES,
                persist=True,
                verbose=False,
                tracker=TRACKER_CONFIG,
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

                send_servo_command(servo_sock, pi_ip, servo_port, pan_angle, tilt_angle)
                if editor is not None:
                    editor.live_marker_x = max(pan_frac, tilt_frac)
            elif editor is not None:
                editor.live_marker_x = None

            if first_frame:
                first_frame = False  # first interval spans startup, not a real frame period
            else:
                inst_fps = 1.0 / max(dt, 1e-6)
                fps = inst_fps if fps == 0.0 else 0.9 * fps + 0.1 * inst_fps  # seed, then smooth
            prev_time = now
            status = "ON" if auto_tracking else "OFF"
            cv2.putText(frame, f"FPS: {fps:.1f}  auto-tracking: {status}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"pan={pan_angle:.1f} ({pan_velocity:+.1f} deg/s)  "
                                f"tilt={tilt_angle:.1f} ({tilt_velocity:+.1f} deg/s)", (20, 690),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

            cv2.imshow("Surfcam prototype - local closed-loop tracking", frame)
            if editor is not None:
                editor.render()
    finally:
        running = False
        cap.release()
        servo_sock.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
