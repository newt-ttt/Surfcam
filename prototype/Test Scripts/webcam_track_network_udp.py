"""
Surfcam prototype - Phase 2 test, low-latency variant: live YOLOv8 person
detection + tracking on frames received directly over UDP from the Pi
(pi/stream_webcam_udp.py), instead of pulling an HTTP MJPEG stream (see
webcam_track_network.py, the earlier version).

A background thread continuously drains the UDP socket and decodes each
arriving datagram into a shared "latest frame". The main thread (running
YOLO inference + display) always grabs whatever's newest rather than
working through a backlog, so if detection briefly falls behind the
incoming frame rate, it skips stale frames instead of accumulating lag.

Usage:
    python webcam_track_network_udp.py [port]
    # port defaults to 5005, must match stream_webcam_udp.py on the Pi
    # this desktop's firewall must allow inbound UDP on this port -
    # Windows will likely prompt for this the first time it runs, or add
    # a rule manually if it doesn't

Controls:
    q - quit
"""

import socket
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_NAME = str(MODELS_DIR / "yolo26n.pt")
PERSON_CLASS_ID = 0
DEFAULT_PORT = 5005
RECV_BUFFER_SIZE = 65536

latest_frame = None
frame_lock = threading.Lock()
frame_ready = threading.Event()
running = True


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


def main():
    global running
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

    model = YOLO(MODEL_NAME)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"Listening for UDP frames on port {port}")

    receiver = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    receiver.start()

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            # Block until a genuinely new frame has arrived instead of
            # re-processing/re-displaying whatever's already in latest_frame -
            # without this, the loop (and the FPS readout below) just measures
            # how fast this desktop can re-run YOLO on a stale frame, not how
            # fast frames are actually arriving from the Pi.
            got_new = frame_ready.wait(timeout=0.5)
            if not got_new:
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue
            frame_ready.clear()

            with frame_lock:
                frame = latest_frame.copy() if latest_frame is not None else None

            if frame is None:
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            h, w = frame.shape[:2]
            frame_cx, frame_cy = w // 2, h // 2

            results = model.track(
                frame,
                classes=[PERSON_CLASS_ID],
                persist=True,
                verbose=False,
            )
            result = results[0]

            # Pick the target: largest bounding box (closest / most prominent person)
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

            # Draw all detections faintly, target in bright green
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    is_target = (x1, y1, x2, y2) == target_box
                    color = (0, 255, 0) if is_target else (100, 100, 100)
                    thickness = 2 if is_target else 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            cv2.drawMarker(frame, (frame_cx, frame_cy), (0, 0, 255),
                            markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

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

            now = time.time()
            fps = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Surfcam prototype - person tracking (UDP)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        running = False
        sock.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
