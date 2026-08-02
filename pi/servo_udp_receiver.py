"""
Surfcam prototype - Pi-side servo UDP receiver.

Listens for pan/tilt angle commands sent from the desktop over UDP and
drives both servos via hardware PWM (rpi_hardware_pwm.HardwarePWM) - see
hold_test.py's docstring for why hardware PWM instead of gpiozero/lgpio.

This validates the desktop -> Pi control link (the opposite direction of
stream_webcam_udp.py, which sends video Pi -> desktop) before the webcam
is physically mounted on the rig, so servo response can be confirmed over
WiFi independent of any CV/tracking code.

Run this ON the Raspberry Pi.

Usage:
    python3 servo_udp_receiver.py [port]   # default port 6000

Each incoming UDP packet is 8 bytes: two big-endian floats (pan_angle,
tilt_angle), matching prototype/servo_control_test.py's PACKET_FORMAT.
Both angles are clamped to SAFE_RANGE before being applied here - a
stray, corrupted, or buggy command from the sender can't drive a servo
past its mapped-safe limits.

Each packet is an absolute target angle, but packets only arrive at the
sender's frame rate (10-20Hz). Rather than snapping the PWM duty cycle
straight to each new target, a fixed-rate tick loop (TICK_HZ) slews the
current angle toward the latest received target at up to SLEW_DEG_S -
see smooth_pan_test.py for the same stepping idea applied to a fixed sweep
instead of incoming commands.
"""

import socket
import struct
import sys

from rpi_hardware_pwm import HardwarePWM

PAN_CHANNEL = 0   # GPIO18
TILT_CHANNEL = 1  # GPIO19
FREQUENCY_HZ = 50
PERIOD_US = 1_000_000 / FREQUENCY_HZ  # 20000us at 50Hz

# Electrical full-scale range the pulse-width formula below is calibrated
# against - NOT the same as a given servo's actual safe range, which comes
# from SAFE_RANGE below.
ELECTRICAL_MIN_ANGLE = -90
ELECTRICAL_MAX_ANGLE = 90
MIN_PULSE_US = 500
MAX_PULSE_US = 2500

# Same ranges as servo_test.py/hold_test.py. Tilt reflects the 2026-07-22
# remap after the original SG90 melted and was replaced. Positive angle =
# tilt down, negative = tilt up (the original convention - a brief report
# that it had flipped was itself mistaken, confirmed via actual auto-
# tracking runs).
SAFE_RANGE = {
    PAN_CHANNEL: (-80, 80),
    TILT_CHANNEL: (-40, 10),
}

DEFAULT_PORT = 6000
PACKET_FORMAT = struct.Struct(">ff")  # pan_angle, tilt_angle

# Interpolation tick rate - independent of both the PWM frequency and the
# sender's frame rate, just needs to be fast enough that stepping looks
# continuous. SLEW_DEG_S should stay above tracking_tuning.json's configured
# max speeds so this never lags behind the spring-follow controller, it
# should only be filling the gaps between sparse command arrivals.
TICK_HZ = 50
TICK_INTERVAL_S = 1 / TICK_HZ
SLEW_DEG_S = 90

# Default angle applied on startup, before any command has arrived. Tilt
# defaults to -30, not the mechanical calibration zero (0) - with the
# camera actually mounted, -30 is what puts the camera roughly straight
# ahead in practice, confirmed empirically 2026-07-22. Within the -40/+10
# safe range.
DEFAULT_ANGLE = {
    PAN_CHANNEL: 0,
    TILT_CHANNEL: -30,
}


def angle_to_duty_percent(angle):
    span = ELECTRICAL_MAX_ANGLE - ELECTRICAL_MIN_ANGLE
    pulse_us = MIN_PULSE_US + (angle - ELECTRICAL_MIN_ANGLE) / span * (MAX_PULSE_US - MIN_PULSE_US)
    return (pulse_us / PERIOD_US) * 100


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def step_toward(current, target, max_step):
    if current < target:
        return min(current + max_step, target)
    return max(current - max_step, target)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

    pwms = {
        PAN_CHANNEL: HardwarePWM(pwm_channel=PAN_CHANNEL, hz=FREQUENCY_HZ, chip=0),
        TILT_CHANNEL: HardwarePWM(pwm_channel=TILT_CHANNEL, hz=FREQUENCY_HZ, chip=0),
    }
    for channel, pwm in pwms.items():
        pwm.start(angle_to_duty_percent(DEFAULT_ANGLE[channel]))
    print(f"Pan at {DEFAULT_ANGLE[PAN_CHANNEL]} degrees, tilt at {DEFAULT_ANGLE[TILT_CHANNEL]} "
          f"degrees (camera roughly level).")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.settimeout(TICK_INTERVAL_S)
    print(f"Listening for servo commands on port {port}")

    current_angle = dict(DEFAULT_ANGLE)
    target_angle = dict(DEFAULT_ANGLE)
    max_step = SLEW_DEG_S * TICK_INTERVAL_S

    try:
        while True:
            try:
                data, addr = sock.recvfrom(PACKET_FORMAT.size)
                if len(data) == PACKET_FORMAT.size:
                    pan_angle, tilt_angle = PACKET_FORMAT.unpack(data)
                    pan_lo, pan_hi = SAFE_RANGE[PAN_CHANNEL]
                    tilt_lo, tilt_hi = SAFE_RANGE[TILT_CHANNEL]
                    target_angle[PAN_CHANNEL] = clamp(pan_angle, pan_lo, pan_hi)
                    target_angle[TILT_CHANNEL] = clamp(tilt_angle, tilt_lo, tilt_hi)
                    print(f"from {addr[0]}: pan={target_angle[PAN_CHANNEL]:.1f} "
                          f"tilt={target_angle[TILT_CHANNEL]:.1f}")
            except socket.timeout:
                pass

            for channel in (PAN_CHANNEL, TILT_CHANNEL):
                current_angle[channel] = step_toward(current_angle[channel], target_angle[channel], max_step)
                pwms[channel].change_duty_cycle(angle_to_duty_percent(current_angle[channel]))
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        for pwm in pwms.values():
            pwm.stop()
        sock.close()


if __name__ == "__main__":
    main()
