"""
Surfcam prototype - standalone smoke test for the speed curve editor
(speed_curve.CurveEditor), with no camera/Pi/network required. Useful for
trying out the k/x0 trackbars and confirming changes persist to
prototype/tracking_tuning.json before wiring it into the full tracking loop.

A marker sweeps back and forth across the curve on its own, standing in
for where a live pixel-distance fraction would sit during real tracking,
so you can see how a given curve shape would translate to a speed cap.

Usage:
    python test_curve_editor.py

Controls:
    q - quit
"""

import math
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from speed_curve import CurveEditor, TuningConfig

TUNING_CONFIG_PATH = Path(__file__).resolve().parent.parent / "tracking_tuning.json"


def main():
    tuning = TuningConfig.load(TUNING_CONFIG_PATH)
    editor = CurveEditor(tuning, TUNING_CONFIG_PATH)
    print(f"Editing {TUNING_CONFIG_PATH}")
    print("Drag the k/x0 trackbars in the curve window. Press 'q' to quit.")

    start = time.time()
    try:
        while True:
            key = cv2.waitKey(30) & 0xFF
            if key == ord("q"):
                break

            # Sweep the marker 0..1..0 so you can see the curve's shape
            # translate into a speed-cap value as "distance" changes.
            t = time.time() - start
            frac = (math.sin(t) + 1) / 2
            editor.live_marker_x = frac
            editor.render()
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
