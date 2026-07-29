"""
Surfcam prototype - Pi-side webcam UDP streaming (low-latency version).

Sends JPEG-encoded frames directly over UDP to the desktop, instead of
serving an HTTP MJPEG stream (see stream_webcam.py, the earlier version).
UDP sendto() never blocks waiting on the receiver, so there's no
equivalent of HTTP/TCP's "server stalls writing to a slow client, frames
back up and go stale" problem - each captured frame is sent immediately
and independently, and a dropped/late packet just costs one missed frame
rather than delaying everything after it. This trades guaranteed delivery
for lower latency, which is the right trade for a live tracking feed
where a frame that arrives late is worse than one that never arrives.

A background thread continuously reads frames from the camera into a
shared "latest frame" slot, independent of how long encode+send takes for
the previous one. The main loop just grabs whatever's freshest whenever
it's ready to send - so a slow JPEG encode no longer delays the next
capture, and a capture that arrives mid-encode isn't queued up behind it.

Run this ON the Raspberry Pi.

One-time setup on the Pi (same as stream_webcam.py):
    sudo apt install python3-opencv
    # if missing/too old: pip3 install opencv-python-headless --break-system-packages

IMPORTANT: the desktop is now the one accepting incoming packets (the Pi
pushes to it), so the desktop needs an inbound firewall rule allowing UDP
on the port used here - Windows Firewall blocks unsolicited inbound UDP
by default. This is the opposite of the HTTP version, where the desktop
was a client pulling from the Pi and needed no firewall changes.

Usage:
    python3 stream_webcam_udp.py <desktop-ip> [port] [bind-ip]
    # e.g. python3 stream_webcam_udp.py 192.168.1.50
    # port defaults to 5005, must match webcam_track_network_udp.py
    # bind-ip pins the socket to one interface. Optional - wlan1 (5GHz)
    # is already the default route. Get its IP via `ip -4 addr show wlan1`.
"""

import socket
import sys
import threading
import time

import cv2

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_FPS = 25  # also enforced in software (MIN_SEND_INTERVAL) - cap.set
# alone isn't reliably honored by this camera/driver
JPEG_QUALITY = 45  # lowered from 70 - 720p frames at 70 were routinely
# exceeding MAX_DATAGRAM_BYTES and getting dropped
DEFAULT_PORT = 5005
MIN_SEND_INTERVAL = 1.0 / FRAME_FPS

# UDP datagrams above ~60KB risk IP fragmentation - if any one fragment is
# lost, the whole frame is lost. Keeping resolution/quality modest keeps
# typical frame size well under that, so this is a safety cap, not a tuning
# knob to raise casually.
MAX_DATAGRAM_BYTES = 60000

latest_frame = None
frame_lock = threading.Lock()
running = True


def capture_loop(cap):
    global latest_frame
    while running:
        ok, frame = cap.read()
        if not ok:
            continue
        with frame_lock:
            latest_frame = frame


def open_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FRAME_FPS)
    # Let auto-exposure/auto-white-balance settle before sending starts.
    for _ in range(15):
        cap.read()
    return cap


def main():
    global running
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 stream_webcam_udp.py <desktop-ip> [port]")
    desktop_ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    bind_ip = sys.argv[3] if len(sys.argv) > 3 else None

    cap = open_camera()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if bind_ip:
        sock.bind((bind_ip, 0))
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]

    capture_thread = threading.Thread(target=capture_loop, args=(cap,), daemon=True)
    capture_thread.start()

    bind_note = f", bound to {bind_ip}" if bind_ip else ""
    print(f"Sending UDP frames to {desktop_ip}:{port}, capped at {FRAME_FPS} fps{bind_note}")
    sent = 0
    dropped_oversize = 0
    frame_counter = 0
    last_send_time = 0.0
    try:
        while True:
            # Software fps cap, paced with a sleep instead of a busy spin -
            # capture now runs independently in its own thread, so this loop
            # is no longer blocked on cap.read() between iterations.
            now = time.time()
            wait = MIN_SEND_INTERVAL - (now - last_send_time)
            if wait > 0:
                time.sleep(wait)

            with frame_lock:
                frame = latest_frame.copy() if latest_frame is not None else None
            if frame is None:
                continue
            last_send_time = time.time()

            # Diagnostic: burned into the pixels so it survives encode/decode -
            # if this ever visibly jumps backward or repeats on the desktop
            # display, frames are arriving out of order over UDP. If it always
            # counts up smoothly, the frame data itself is fine and any visual
            # "wiggle" is a display-side (cv2.imshow) tearing artifact instead.
            frame_counter += 1
            cv2.putText(frame, f"seq={frame_counter}", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            ok, buf = cv2.imencode(".jpg", frame, encode_params)
            if not ok:
                continue
            data = buf.tobytes()
            if len(data) > MAX_DATAGRAM_BYTES:
                dropped_oversize += 1
                continue
            sock.sendto(data, (desktop_ip, port))
            sent += 1
            if sent % 100 == 0:
                print(f"sent={sent} dropped_oversize={dropped_oversize}")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        running = False
        cap.release()
        sock.close()


if __name__ == "__main__":
    main()
