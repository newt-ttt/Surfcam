"""
Surfcam prototype - normalized speed-cap curve, backed by a small set of
draggable control points, plus a live OpenCV editor window for it.

The curve maps a 0..1 pixel-distance fraction (how far off-center a target
is, relative to that axis's half-frame extent) to a 0..1 speed-cap fraction.
tracking_servo_control.py scales that fraction by a per-axis max-speed
constant to get an actual velocity cap (deg/s) for its spring-follow
controller. Pan and tilt reuse the same curve shape; only the max-speed
scale differs per axis.

Editing: drag a point to move it, double-click empty space to add a point,
double-click an existing (non-endpoint) point to remove it. Endpoints stay
pinned to x=0/x=1 (the curve must be defined across the full range) but
their y value is draggable. Edits apply immediately to the live curve;
they're written to disk once a drag/edit completes, not on every mouse-move.
"""

import json

import cv2
import numpy as np

DEFAULT_POINTS = [[0.0, 0.0], [1.0, 1.0]]
POINT_PICK_RADIUS = 0.04  # fraction-space hit radius for grabbing a point

WINDOW_NAME = "Speed curve (drag points, dbl-click to add/remove)"
CANVAS_SIZE = (460, 360)  # width, height in pixels
MARGIN_LEFT = 55   # room for y tick labels + axis title
MARGIN_RIGHT = 20
MARGIN_TOP = 20
MARGIN_BOTTOM = 55  # room for x tick labels + axis title


class SpeedCurve:
    def __init__(self, points=None):
        self.points = sorted((list(p) for p in (points or DEFAULT_POINTS)), key=lambda p: p[0])

    def value(self, x):
        x = min(max(x, 0.0), 1.0)
        pts = self.points
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                if x1 == x0:
                    return y1
                t = (x - x0) / (x1 - x0)
                return y0 + t * (y1 - y0)
        return pts[-1][1]

    def move_point(self, index, x, y):
        pts = self.points
        if index in (0, len(pts) - 1):
            x = pts[index][0]  # endpoints stay pinned to x=0 / x=1
        else:
            lo = pts[index - 1][0]
            hi = pts[index + 1][0]
            x = min(max(x, lo + 1e-3), hi - 1e-3)
        pts[index] = [x, min(max(y, 0.0), 1.0)]

    def add_point(self, x, y):
        x = min(max(x, 0.0), 1.0)
        y = min(max(y, 0.0), 1.0)
        self.points.append([x, y])
        self.points.sort(key=lambda p: p[0])

    def remove_point(self, index):
        if 0 < index < len(self.points) - 1:
            del self.points[index]

    def find_near(self, x, y, radius=POINT_PICK_RADIUS):
        for i, (px, py) in enumerate(self.points):
            if abs(px - x) <= radius and abs(py - y) <= radius:
                return i
        return None


class TuningConfig:
    def __init__(self, curve=None, omega_n=6.0, zeta=1.0,
                 pan_max_speed_deg_s=8.0, tilt_max_speed_deg_s=4.0):
        self.curve = curve or SpeedCurve()
        self.omega_n = omega_n
        self.zeta = zeta
        self.pan_max_speed_deg_s = pan_max_speed_deg_s
        self.tilt_max_speed_deg_s = tilt_max_speed_deg_s

    @classmethod
    def load(cls, path):
        if not path.exists():
            config = cls()
            config.save(path)
            return config
        data = json.loads(path.read_text())
        config = cls(
            curve=SpeedCurve(data.get("curve_points")),
            omega_n=data.get("omega_n", 6.0),
            zeta=data.get("zeta", 1.0),
            pan_max_speed_deg_s=data.get("pan_max_speed_deg_s", 8.0),
            tilt_max_speed_deg_s=data.get("tilt_max_speed_deg_s", 4.0),
        )
        return config

    def save(self, path):
        path.write_text(json.dumps({
            "curve_points": self.curve.points,
            "omega_n": self.omega_n,
            "zeta": self.zeta,
            "pan_max_speed_deg_s": self.pan_max_speed_deg_s,
            "tilt_max_speed_deg_s": self.tilt_max_speed_deg_s,
        }, indent=2))


class CurveEditor:
    """Second OpenCV window for live-dragging the speed curve. Call
    render() once per main loop iteration, alongside the video window's
    own imshow/waitKey - both windows are polled by the same waitKey."""

    def __init__(self, config, config_path):
        self.config = config
        self.config_path = config_path
        self.dragging = None
        self.live_marker_x = None  # set externally each frame; None hides it
        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self._on_mouse)

    def _to_frac(self, px, py):
        w, h = CANVAS_SIZE
        plot_w = w - MARGIN_LEFT - MARGIN_RIGHT
        plot_h = h - MARGIN_TOP - MARGIN_BOTTOM
        x = (px - MARGIN_LEFT) / plot_w
        y = 1.0 - (py - MARGIN_TOP) / plot_h
        return x, y

    def _to_px(self, x, y):
        w, h = CANVAS_SIZE
        plot_w = w - MARGIN_LEFT - MARGIN_RIGHT
        plot_h = h - MARGIN_TOP - MARGIN_BOTTOM
        px = MARGIN_LEFT + x * plot_w
        py = MARGIN_TOP + (1.0 - y) * plot_h
        return int(px), int(py)

    def _draw_vertical_text(self, canvas, text, x, y_center, font_scale=0.4, color=(150, 150, 150)):
        """Draws text rotated 90deg (bottom-to-top), for the y-axis title."""
        (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        pad = 4
        text_img = np.full((th + baseline + pad, tw + pad, 3), 30, dtype=np.uint8)
        cv2.putText(text_img, text, (pad // 2, th + pad // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1, cv2.LINE_AA)
        rotated = cv2.rotate(text_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        rh, rw = rotated.shape[:2]
        y0 = max(0, min(int(y_center - rh / 2), canvas.shape[0] - rh))
        x0 = max(0, min(int(x), canvas.shape[1] - rw))
        canvas[y0:y0 + rh, x0:x0 + rw] = rotated

    def _on_mouse(self, event, px, py, _flags, _userdata):
        x, y = self._to_frac(px, py)
        curve = self.config.curve
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = curve.find_near(x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging is not None:
            curve.move_point(self.dragging, x, y)
        elif event == cv2.EVENT_LBUTTONUP and self.dragging is not None:
            curve.move_point(self.dragging, x, y)
            self.dragging = None
            self.config.save(self.config_path)
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            near = curve.find_near(x, y)
            if near is not None:
                curve.remove_point(near)
            else:
                curve.add_point(x, y)
            self.config.save(self.config_path)

    def render(self):
        w, h = CANVAS_SIZE
        frame = np.full((h, w, 3), 30, dtype=np.uint8)
        plot_top = MARGIN_TOP
        plot_bottom = h - MARGIN_BOTTOM
        plot_left = MARGIN_LEFT
        plot_right = w - MARGIN_RIGHT

        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            gx, _ = self._to_px(frac, 0)
            _, gy = self._to_px(0, frac)
            cv2.line(frame, (gx, plot_top), (gx, plot_bottom), (60, 60, 60), 1)
            cv2.line(frame, (plot_left, gy), (plot_right, gy), (60, 60, 60), 1)

            label = f"{frac:g}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            # x tick labels, centered under each gridline
            cv2.putText(frame, label, (gx - tw // 2, plot_bottom + th + 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1, cv2.LINE_AA)
            # y tick labels, right-aligned to the left of the plot
            cv2.putText(frame, label, (plot_left - tw - 8, gy + th // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1, cv2.LINE_AA)

        cv2.rectangle(frame, (plot_left, plot_top), (plot_right, plot_bottom), (90, 90, 90), 1)

        curve = self.config.curve
        prev = None
        for step in range(0, 101):
            x = step / 100
            pt = self._to_px(x, curve.value(x))
            if prev is not None:
                cv2.line(frame, prev, pt, (0, 200, 255), 2)
            prev = pt

        for x, y in curve.points:
            cv2.circle(frame, self._to_px(x, y), 5, (0, 255, 0), -1)

        if self.live_marker_x is not None:
            mx, _ = self._to_px(self.live_marker_x, 0)
            cv2.line(frame, (mx, plot_top), (mx, plot_bottom), (255, 0, 255), 1)

        x_title = "distance from center (fraction of half-frame)"
        (xt_w, _), _ = cv2.getTextSize(x_title, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(frame, x_title, ((plot_left + plot_right) // 2 - xt_w // 2, h - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)

        self._draw_vertical_text(frame, "speed cap (fraction of axis max)", 4,
                                  (plot_top + plot_bottom) // 2, font_scale=0.42, color=(200, 200, 200))

        cv2.imshow(WINDOW_NAME, frame)
