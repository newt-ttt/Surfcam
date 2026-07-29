"""
Surfcam prototype - Phase 2 test: live YOLOv8 person detection + tracking
on the C270, streamed over the network from the Raspberry Pi (pi/stream_
webcam.py) instead of a USB webcam plugged directly into this desktop.

Same detection/overlay logic as webcam_track.py - only the frame source
changed, from a local DirectShow/MSMF device to an HTTP MJPEG stream. No
servos involved yet; this validates the Pi -> desktop video pipeline
before wiring the webcam onto the pan/tilt rig.

Usage:
    python webcam_track_network.py <pi-ip> [port]
    # e.g. python webcam_track_network.py 192.168.1.42
    # port defaults to 8080, matching pi/stream_webcam.py's default

Controls:
    q - quit
"""

import sys
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
# yolo26n.pt: newer generation, smaller (2.4M params), higher mAP, and faster
# (NMS-free) than yolov8n.pt - see research discussion. Swap back to
# "yolov8n.pt" here to A/B compare; both use the same 80-class COCO labels.
MODEL_NAME = str(MODELS_DIR / "yolo26n.pt")
PERSON_CLASS_ID = 0
DEFAULT_PORT = 8080


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python webcam_track_network.py <pi-ip> [port]")
    pi_ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    stream_url = f"http://{pi_ip}:{port}/video_feed"

    model = YOLO(MODEL_NAME)

    print(f"Connecting to {stream_url}")
    cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open stream at {stream_url} - is stream_webcam.py "
            f"running on the Pi, and is this desktop on the same network?"
        )

    prev_time = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to grab frame")
            break

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

        # Frame center crosshair
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

        cv2.imshow("Surfcam prototype - person tracking (networked)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
