"""
Surfcam prototype - Phase 2 test: send pan/tilt servo commands from this
desktop to the Pi over UDP (pi/servo_udp_receiver.py), and confirm the rig
responds correctly over WiFi - before the webcam is physically mounted on
it, so servo control can be validated independent of any CV/tracking.

Same interactive control scheme as pi/servo_test.py, just sent over the
network as absolute pan/tilt angles instead of driving GPIO locally. The
Pi independently re-clamps both angles to its own SAFE_RANGE before
applying them, so this script's own clamping is a courtesy for a sane
on-screen readout, not the only safety net.

Usage:
    python servo_control_test.py <pi-ip> [port]
    # port defaults to 6000, must match servo_udp_receiver.py on the Pi

Controls:
    +       nudge the active servo's angle up by 10 degrees (clamped)
    -       nudge the active servo's angle down by 10 degrees (clamped)
    c       recenter the active servo (0 degrees)
    p       switch active servo to pan
    t       switch active servo to tilt
    q       quit
"""

import socket
import struct
import sys

PAN = "pan"
TILT = "tilt"
DEFAULT_PORT = 6000
STEP_DEG = 10

# Mirrors pi/servo_udp_receiver.py's SAFE_RANGE - the Pi re-clamps
# independently, but matching ranges here means what's shown on screen is
# what actually gets applied, rather than being silently re-clamped there.
SAFE_RANGE = {
    PAN: (-80, 80),
    TILT: (-40, 10),
}

PACKET_FORMAT = struct.Struct(">ff")  # pan_angle, tilt_angle

# Matches pi/servo_udp_receiver.py's DEFAULT_ANGLE - keeps this tool's
# initial state in sync with what the Pi is already sitting at on startup,
# so opening this tool doesn't immediately send an override back to 0.
DEFAULT_ANGLE = {
    PAN: 0.0,
    TILT: -30.0,
}


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python servo_control_test.py <pi-ip> [port]")
    pi_ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    angle = {PAN: DEFAULT_ANGLE[PAN], TILT: DEFAULT_ANGLE[TILT]}
    active = PAN

    def send():
        data = PACKET_FORMAT.pack(angle[PAN], angle[TILT])
        sock.sendto(data, (pi_ip, port))

    send()
    print(f"Sending commands to {pi_ip}:{port}")
    print(f"Pan at {DEFAULT_ANGLE[PAN]:.0f} degrees, tilt at {DEFAULT_ANGLE[TILT]:.0f} "
          f"degrees (camera roughly level).")
    print("Controls: + / - nudge 10deg, c recenter, p=pan, t=tilt, q=quit\n")

    try:
        while True:
            lo, hi = SAFE_RANGE[active]
            print(f"[{active}] angle={angle[active]:.0f}deg "
                  f"(safe range {lo} to {hi})  > ", end="")
            cmd = input().strip().lower()

            if cmd == "q":
                break
            elif cmd == "p":
                active = PAN
            elif cmd == "t":
                active = TILT
            elif cmd == "c":
                angle[active] = DEFAULT_ANGLE[active]
                send()
            elif cmd == "+":
                lo, hi = SAFE_RANGE[active]
                angle[active] = min(hi, angle[active] + STEP_DEG)
                send()
            elif cmd == "-":
                lo, hi = SAFE_RANGE[active]
                angle[active] = max(lo, angle[active] - STEP_DEG)
                send()
            else:
                print("unrecognized command (use +, -, c, p, t, or q)")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
