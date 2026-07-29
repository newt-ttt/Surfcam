"""
Surfcam prototype - Pi-side smooth pan sweep test (hardware PWM version).

Ramps a servo gradually between its mapped safe extremes, in small angle
steps with a short sleep between each, instead of jumping straight to a
target angle like hold_test.py/servo_test.py do. Useful to check how
smoothly the rig can pan at a given angular speed before deciding how the
eventual PID loop should rate-limit its output - a raw servo has no
built-in speed control, it just chases whatever angle it's told as fast
as the hardware allows, so "slow and smooth" has to be implemented by
stepping the commanded angle gradually, exactly like this script does.

Run this ON the Raspberry Pi.

Usage:
    python3 smooth_pan_test.py            # pan, default speed (20 deg/sec)
    python3 smooth_pan_test.py 40         # pan at 40 deg/sec
    python3 smooth_pan_test.py 40 1       # tilt (channel 1) at 40 deg/sec

Ctrl+C to stop early (still stops the PWM channel cleanly).
"""

import sys
import time

from rpi_hardware_pwm import HardwarePWM

PAN_CHANNEL = 0   # GPIO18
TILT_CHANNEL = 1  # GPIO19
FREQUENCY_HZ = 50
PERIOD_US = 1_000_000 / FREQUENCY_HZ  # 20000us at 50Hz

ELECTRICAL_MIN_ANGLE = -90
ELECTRICAL_MAX_ANGLE = 90
MIN_PULSE_US = 500
MAX_PULSE_US = 2500

# Same mapped safe ranges as servo_test.py/hold_test.py. Tilt remapped
# 2026-07-22 after the original SG90 melted and was replaced with a new
# unit whose mounted zero position differs from the old one.
SAFE_RANGE = {
    PAN_CHANNEL: (-80, 80),
    TILT_CHANNEL: (-40, 10),
}

DEFAULT_DEG_PER_SEC = 20
STEP_DEG = 1  # angular resolution per update - smaller = smoother
SWEEPS = 3    # number of full back-and-forth cycles


def angle_to_duty_percent(angle):
    span = ELECTRICAL_MAX_ANGLE - ELECTRICAL_MIN_ANGLE
    pulse_us = MIN_PULSE_US + (angle - ELECTRICAL_MIN_ANGLE) / span * (MAX_PULSE_US - MIN_PULSE_US)
    return (pulse_us / PERIOD_US) * 100


def sweep_to(pwm, current_angle, target_angle, deg_per_sec):
    step_interval = STEP_DEG / deg_per_sec
    direction = 1 if target_angle > current_angle else -1
    angle = current_angle
    while angle != target_angle:
        angle += direction * STEP_DEG
        if (direction == 1 and angle > target_angle) or (direction == -1 and angle < target_angle):
            angle = target_angle
        pwm.change_duty_cycle(angle_to_duty_percent(angle))
        time.sleep(step_interval)
    return angle


def main():
    deg_per_sec = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DEG_PER_SEC
    channel = int(sys.argv[2]) if len(sys.argv) > 2 else PAN_CHANNEL
    lo, hi = SAFE_RANGE[channel]
    label = "pan" if channel == PAN_CHANNEL else "tilt"

    pwm = HardwarePWM(pwm_channel=channel, hz=FREQUENCY_HZ, chip=0)
    pwm.start(angle_to_duty_percent(0))
    angle = 0
    print(f"Sweeping {label} (channel {channel}) between {lo} and {hi} degrees "
          f"at {deg_per_sec} deg/sec, {SWEEPS} full cycles. Ctrl+C to stop.")

    try:
        for i in range(SWEEPS):
            print(f"cycle {i + 1}: -> {hi}")
            angle = sweep_to(pwm, angle, hi, deg_per_sec)
            print(f"cycle {i + 1}: -> {lo}")
            angle = sweep_to(pwm, angle, lo, deg_per_sec)
    except KeyboardInterrupt:
        print("\nStopped early.")
    finally:
        pwm.stop()
        print(f"{label}: stopped")


if __name__ == "__main__":
    main()
