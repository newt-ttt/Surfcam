"""
Surfcam prototype - face detection test (YOLOv8n-face, Bingsu/adetailer weights)
on the Logitech C270, same overlay/error-signal setup as webcam_track.py.

Not part of the surf tracking pipeline itself (see webcam_track.py's docstring
for why "person" is the right class for surf, not "face") - this is just a
side test of a different YOLOv8 model to see how face-specific detection
behaves vs. general person detection.

Controls:
  q - quit
"""

import time
from pathlib import Path

import cv2
from pygrabber.dshow_graph import FilterGraph
from ultralytics import YOLO

CAMERA_NAME_HINT = "C270"
MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "training" / "models" / "face" / "face_yolov8n.pt"


def find_camera_index(name_hint: str) -> int:
    devices = FilterGraph().get_input_devices()
    for i, name in enumerate(devices):
        if name_hint.lower() in name.lower():
            return i
    raise RuntimeError(
        f"No camera matching '{name_hint}' found. Available devices: {devices}"
    )


def main():
    model = YOLO(str(MODEL_PATH))
    print(f"Model classes: {model.names}")

    camera_index = find_camera_index(CAMERA_NAME_HINT)
    print(f"Using camera index {camera_index} (matched '{CAMERA_NAME_HINT}')")

    cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {camera_index}")

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    for _ in range(15):
        cap.read()

    prev_time = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to grab frame")
            break

        h, w = frame.shape[:2]
        frame_cx, frame_cy = w // 2, h // 2

        results = model.track(frame, persist=True, verbose=False)
        result = results[0]

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
            cv2.putText(frame, "no face", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        now = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
        prev_time = now
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Surfcam prototype - face tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
