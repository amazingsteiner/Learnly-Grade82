import math
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF
from PySide6.QtWidgets import QWidget, QSizePolicy


class DiagramCanvas(QWidget):
    """Renders a diagram dict (from QuestionEngine) automatically. No manual images needed."""

    def __init__(self, diagram=None, parent=None):
        super().__init__(parent)
        self.diagram = diagram
        self.setMinimumSize(300, 260)

    def set_diagram(self, diagram):
        self.diagram = diagram
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#ffffff"))
        if not self.diagram:
            return
        d = self.diagram
        kind = d.get("type")
        w, h = self.width(), self.height()
        pen = QPen(QColor("#3157D5"), 3)
        p.setPen(pen)
        font = QFont("Sans", 11, QFont.Bold)
        p.setFont(font)

        if kind == "right_triangle":
            margin = 40
            base = min(w, h) - 2 * margin
            x0, y0 = margin, h - margin
            p.drawLine(QPointF(x0, y0), QPointF(x0 + base, y0))          # base
            p.drawLine(QPointF(x0, y0), QPointF(x0, y0 - base * 0.75))    # height
            p.drawLine(QPointF(x0 + base, y0), QPointF(x0, y0 - base * 0.75))  # hypotenuse
            # right angle marker
            p.drawRect(QRectF(x0, y0 - 14, 14, 14))
            a = d.get("a", "?"); b = d.get("b", "?"); c = d.get("c", "?")
            find = d.get("find")
            p.drawText(QPointF(x0 + base / 2 - 10, y0 + 22), f"{a if find!='a' else 'a'} cm" if "a" in d else "")
            p.drawText(QPointF(x0 - 34, y0 - base * 0.35), f"{b if find!='b' else '?'} cm" if "b" in d else "")
            p.drawText(QPointF(x0 + base / 2 - 10, y0 - base * 0.45), f"{c if find!='c' else '?'} cm" if "c" in d else "")

        elif kind == "triangle_bh":
            margin = 40
            base = min(w, h) - 2 * margin
            x0, y0 = margin, h - margin
            apex = QPointF(x0 + base * 0.4, y0 - base * 0.7)
            p.drawLine(QPointF(x0, y0), QPointF(x0 + base, y0))
            p.drawLine(QPointF(x0, y0), apex)
            p.drawLine(QPointF(x0 + base, y0), apex)
            dash = QPen(QColor("#999999"), 1, Qt.DashLine)
            p.setPen(dash)
            p.drawLine(apex, QPointF(apex.x(), y0))
            p.setPen(pen)
            p.drawText(QPointF(x0 + base / 2 - 20, y0 + 22), f"base = {d.get('b','?')} cm")
            p.drawText(QPointF(apex.x() + 6, (apex.y() + y0) / 2), f"h = {d.get('h','?')} cm")

        elif kind == "rectangle":
            margin = 40
            rw = min(w - 2 * margin, 220)
            rh = min(h - 2 * margin, 140)
            x0, y0 = (w - rw) / 2, (h - rh) / 2
            p.drawRect(QRectF(x0, y0, rw, rh))
            p.drawText(QPointF(x0 + rw / 2 - 20, y0 - 10), f"l = {d.get('l','?')} cm")
            p.drawText(QPointF(x0 - 34, y0 + rh / 2), f"w = {d.get('w','?')}")

        elif kind == "circle":
            r_px = min(w, h) / 2 - 40
            cx, cy = w / 2, h / 2
            p.drawEllipse(QPointF(cx, cy), r_px, r_px)
            p.drawLine(QPointF(cx, cy), QPointF(cx + r_px, cy))
            p.drawText(QPointF(cx + r_px / 2 - 10, cy - 6), f"r = {d.get('r','?')} cm")

        elif kind == "straight_line_angles":
            y = h / 2
            p.drawLine(QPointF(30, y), QPointF(w - 30, y))
            vx = w * 0.55
            p.drawLine(QPointF(vx, y), QPointF(vx - 60, y - 70))
            p.drawText(QPointF(vx - 55, y - 40), f"{d.get('known','?')}°")
            p.drawText(QPointF(vx + 10, y - 20), "x")

        elif kind == "angles_at_point":
            cx, cy = w / 2, h / 2
            r = min(w, h) / 2 - 30
            angles = [0, 100, 220]
            for i, ang in enumerate(angles):
                rad = math.radians(ang)
                p.drawLine(QPointF(cx, cy), QPointF(cx + r * math.cos(rad), cy - r * math.sin(rad)))
            p.drawText(QPointF(cx + 20, cy - 30), f"{d.get('a','?')}°")
            p.drawText(QPointF(cx - 60, cy - 30), f"{d.get('b','?')}°")
            p.drawText(QPointF(cx - 20, cy + 45), "y")

        elif kind == "vertical_angles":
            cx, cy = w / 2, h / 2
            r = min(w, h) / 2 - 30
            p.drawLine(QPointF(cx - r, cy - r * 0.4), QPointF(cx + r, cy + r * 0.4))
            p.drawLine(QPointF(cx - r, cy + r * 0.4), QPointF(cx + r, cy - r * 0.4))
            p.drawText(QPointF(cx + 12, cy - 30), f"{d.get('known','?')}°")
            p.drawText(QPointF(cx - 40, cy + 40), "?")

        elif kind in ("translation", "reflect_x", "reflect_y"):
            self._draw_grid(p, w, h)
            scale = min(w, h) / 22
            cx, cy = w / 2, h / 2
            x, y = d.get("x", 0), d.get("y", 0)
            p1 = QPointF(cx + x * scale, cy - y * scale)
            p.setBrush(QBrush(QColor("#3157D5")))
            p.drawEllipse(p1, 6, 6)
            p.drawText(p1 + QPointF(8, -8), f"({x},{y})")
            if kind == "translation":
                a, b = d.get("a", 0), d.get("b", 0)
                p2 = QPointF(cx + (x + a) * scale, cy - (y + b) * scale)
            elif kind == "reflect_x":
                p2 = QPointF(cx + x * scale, cy - (-y) * scale)
            else:
                p2 = QPointF(cx + (-x) * scale, cy - y * scale)
            p.setBrush(QBrush(QColor("#D64545")))
            p.drawEllipse(p2, 6, 6)
            dash = QPen(QColor("#999999"), 1, Qt.DashLine)
            p.setPen(dash)
            p.drawLine(p1, p2)

    def _draw_grid(self, p, w, h):
        pen = QPen(QColor("#e0e0e0"), 1)
        p.setPen(pen)
        step = min(w, h) / 22
        cx, cy = w / 2, h / 2
        x = cx
        while x < w:
            p.drawLine(QPointF(x, 0), QPointF(x, h)); x += step
        x = cx
        while x > 0:
            p.drawLine(QPointF(x, 0), QPointF(x, h)); x -= step
        y = cy
        while y < h:
            p.drawLine(QPointF(0, y), QPointF(w, y)); y += step
        y = cy
        while y > 0:
            p.drawLine(QPointF(0, y), QPointF(w, y)); y -= step
        axis_pen = QPen(QColor("#333333"), 2)
        p.setPen(axis_pen)
        p.drawLine(QPointF(0, cy), QPointF(w, cy))
        p.drawLine(QPointF(cx, 0), QPointF(cx, h))


class GeometryLabCanvas(QWidget):
    """Interactive freeform drawing canvas: tap points to build shapes on a coordinate grid."""

    MODES = ["Point", "Line Segment", "Triangle", "Rectangle", "Circle", "Angle", "Coordinate Plane"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumWidth(280)
        self.mode = "Triangle"
        self.points = []
        self.show_measurements = True

    def clear(self):
        self.points = []
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.points.append(event.position())
            limits = {"Point": 1, "Line Segment": 2, "Triangle": 3, "Rectangle": 2,
                      "Circle": 2, "Angle": 3, "Coordinate Plane": 999}
            limit = limits.get(self.mode, 3)
            if len(self.points) > limit:
                self.points.pop(0)
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#ffffff"))

        # background grid
        grid_pen = QPen(QColor("#eeeeee"), 1)
        p.setPen(grid_pen)
        step = 24
        for gx in range(0, self.width(), step):
            p.drawLine(gx, 0, gx, self.height())
        for gy in range(0, self.height(), step):
            p.drawLine(0, gy, self.width(), gy)

        pen = QPen(QColor("#3157D5"), 3)
        p.setPen(pen)
        font = QFont("Sans", 10, QFont.Bold)
        p.setFont(font)
        pts = self.points

        if self.mode == "Point" and len(pts) >= 1:
            p.setBrush(QBrush(QColor("#3157D5")))
            p.drawEllipse(pts[-1], 5, 5)

        elif self.mode == "Line Segment" and len(pts) >= 2:
            p.drawLine(pts[-2], pts[-1])
            if self.show_measurements:
                dist = math.hypot(pts[-1].x() - pts[-2].x(), pts[-1].y() - pts[-2].y())
                mid = (pts[-2] + pts[-1]) / 2
                p.drawText(mid, f"{dist/24:.1f} u")

        elif self.mode == "Triangle" and len(pts) >= 3:
            poly = QPolygonF(pts[-3:])
            p.drawPolygon(poly)
            if self.show_measurements:
                a, b, c = pts[-3:]
                sides = [(a, b), (b, c), (c, a)]
                for s1, s2 in sides:
                    dist = math.hypot(s2.x() - s1.x(), s2.y() - s1.y())
                    mid = (s1 + s2) / 2
                    p.drawText(mid, f"{dist/24:.1f}u")

        elif self.mode == "Rectangle" and len(pts) >= 2:
            a, b = pts[-2:]
            x, y = min(a.x(), b.x()), min(a.y(), b.y())
            rw, rh = abs(a.x() - b.x()), abs(a.y() - b.y())
            p.drawRect(QRectF(x, y, rw, rh))
            if self.show_measurements:
                p.drawText(QPointF(x + rw / 2, y - 6), f"w={rw/24:.1f}u")
                p.drawText(QPointF(x - 30, y + rh / 2), f"h={rh/24:.1f}u")

        elif self.mode == "Circle" and len(pts) >= 2:
            a, b = pts[-2:]
            r = math.hypot(a.x() - b.x(), a.y() - b.y())
            p.drawEllipse(a, r, r)
            if self.show_measurements:
                p.drawText(a + QPointF(6, -6), f"r={r/24:.1f}u")

        elif self.mode == "Angle" and len(pts) >= 3:
            vertex, p1, p2 = pts[-3:]
            p.drawLine(vertex, p1)
            p.drawLine(vertex, p2)
            v1 = math.atan2(p1.y() - vertex.y(), p1.x() - vertex.x())
            v2 = math.atan2(p2.y() - vertex.y(), p2.x() - vertex.x())
            deg = abs(math.degrees(v2 - v1))
            if deg > 180:
                deg = 360 - deg
            p.drawText(vertex + QPointF(10, 10), f"{deg:.0f}°")

        elif self.mode == "Coordinate Plane":
            axis_pen = QPen(QColor("#333333"), 2)
            p.setPen(axis_pen)
            cx, cy = self.width() / 2, self.height() / 2
            p.drawLine(0, int(cy), self.width(), int(cy))
            p.drawLine(int(cx), 0, int(cx), self.height())
            p.setPen(pen)
            p.setBrush(QBrush(QColor("#3157D5")))
            for pt in pts:
                p.drawEllipse(pt, 4, 4)
                gx = round((pt.x() - cx) / step)
                gy = round((cy - pt.y()) / step)
                p.drawText(pt + QPointF(6, -6), f"({gx},{gy})")
