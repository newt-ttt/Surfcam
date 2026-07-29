#!/bin/bash
# Surfcam - launches both Pi-side processes needed for the desktop<->Pi
# tracking pipeline (video streamer + servo command receiver) from one
# terminal, instead of needing two separate terminal sessions.
#
# Ctrl+C - or either process dying unexpectedly - stops both cleanly
# rather than leaving one running orphaned. Both underlying Python
# scripts already have graceful shutdown logic in their own `finally`
# blocks (releasing the camera, stopping PWM cleanly) that only runs on a
# real KeyboardInterrupt/SIGINT - this script sends SIGINT directly to
# each process (not a blunter kill) so that cleanup logic actually runs.
#
# One-time setup:
#   chmod +x run_both.sh
#
# Usage:
#   ./run_both.sh <desktop-ip> [video_port] [servo_port]
#   e.g. ./run_both.sh 192.168.1.181
#   # video_port defaults to 5005, servo_port defaults to 6000

if [ -z "$1" ]; then
    echo "Usage: $0 <desktop-ip> [video_port] [servo_port]"
    exit 1
fi

DESKTOP_IP="$1"
VIDEO_PORT="${2:-5005}"
SERVO_PORT="${3:-6000}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/stream_webcam_udp.py" "$DESKTOP_IP" "$VIDEO_PORT" &
STREAM_PID=$!

python3 "$SCRIPT_DIR/servo_udp_receiver.py" "$SERVO_PORT" &
SERVO_PID=$!

stop_both() {
    kill -INT "$STREAM_PID" "$SERVO_PID" 2>/dev/null
    wait "$STREAM_PID" "$SERVO_PID" 2>/dev/null
}
trap stop_both SIGINT SIGTERM

echo "Both running (stream pid=$STREAM_PID, servo pid=$SERVO_PID)."
echo "Press Ctrl+C to stop both."

# If either process exits on its own (crash or otherwise), stop the other
# too instead of leaving it running orphaned.
wait -n "$STREAM_PID" "$SERVO_PID"
stop_both
