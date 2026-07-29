"""
Surfcam prototype - Pi-side webcam MJPEG streaming server using ONLY HTTP (early test).

Captures from the C270 (attached to the Pi via USB) and serves it as an
HTTP MJPEG stream (multipart/x-mixed-replace) - the same format a browser
uses to view a live webcam. This means the desktop side just needs
cv2.VideoCapture(url), no GStreamer/RTSP setup on either end.

Run this ON the Raspberry Pi.

One-time setup on the Pi:
    sudo apt install python3-opencv python3-flask
    # if either package is missing/too old on this OS release, fall back to:
    #   pip3 install opencv-python-headless flask --break-system-packages

Usage:
    python3 stream_webcam.py [port]   # default port 8080

Find this Pi's IP (needed on the desktop side) with:
    hostname -I

Then on the desktop, point webcam_track_network.py at:
    python webcam_track_network.py <this-pi-ip>
"""

import sys

import cv2
from flask import Flask, Response

CAMERA_INDEX = 0  # /dev/video0 - only camera on the Pi, no enumeration needed
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_FPS = 10  # hardcoded to match the C270's actual sustained rate on the Pi
JPEG_QUALITY = 80  # 0-100 - lower trades image quality for less wifi bandwidth/latency

app = Flask(__name__)


def open_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")
    # Request the camera's hardware MJPG mode, same reasoning as the desktop
    # script's CAP_MSMF fix: without this, USB bandwidth caps capture at a
    # much lower FPS than the C270 can actually do at 720p.
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FRAME_FPS)
    # Let auto-exposure/auto-white-balance settle before streaming starts.
    for _ in range(15):
        cap.read()
    return cap


def generate_frames():
    cap = open_camera()
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            ok, buf = cv2.imencode(".jpg", frame, encode_params)
            if not ok:
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            )
    finally:
        cap.release()


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/")
def index():
    return "Surfcam Pi stream - see /video_feed"


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Streaming C270 at http://0.0.0.0:{port}/video_feed")
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
