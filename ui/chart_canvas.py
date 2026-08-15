import math
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QWidget

PALETTE = ["#3157D5", "#159A68", "#D64545", "#F5A623", "#8B5CF6", "#06B6D4", "#EC4899"]


class ChartCanvas(QWidget):
    """Bar / Pie / Line / Box-and-whisker chart drawn programmatically (no image assets)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 260)
        self.mode = "bar"
        self.values = []
        self.labels = []

    def set_data(self, values, labels=None, mode="bar"):
        self.values = list(values)
        self.labels = labels or [str(i + 1) for i in range(len(self.values))]
        self.mode = mode
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#ffffff"))
        if not self.values:
            p.drawText(self.rect(), Qt.AlignCenter, "No data yet")
            return
        if self.mode == "bar":
            self._bar(p)
        elif self.mode == "pie":
            self._pie(p)
        elif self.mode == "line":
            self._line(p)
        elif self.mode == "box":
            self._box(p)

    def _bar(self, p):
        w, h = self.width(), self.height()
        margin = 36
        top = 20
        chart_h = h - margin - top
        vmax = max(self.values) or 1
        n = len(self.values)
        bw = (w - 2 * margin) / max(1, n)
        font = QFont("Sans", 9)
        p.setFont(font)
        for i, v in enumerate(self.values):
            bar_h = (v / vmax) * chart_h
            x = margin + i * bw + bw * 0.15
            y = h - margin - bar_h
            color = QColor(PALETTE[i % len(PALETTE)])
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRect(QRectF(x, y, bw * 0.7, bar_h))
            p.setPen(QPen(QColor("#333")))
            p.drawText(QRectF(x - 5, h - margin + 4, bw, 16), Qt.AlignCenter, str(self.labels[i]))
            p.drawText(QRectF(x - 5, y - 16, bw + 10, 14), Qt.AlignCenter, str(v))
        p.setPen(QPen(QColor("#333"), 2))
        p.drawLine(margin, h - margin, w - margin, h - margin)

    def _pie(self, p):
        w, h = self.width(), self.height()
        size = min(w, h) - 70
        rect = QRectF((w - size) / 2, (h - size) / 2 - 10, size, size)
        total = sum(self.values) or 1
        start = 0
        font = QFont("Sans", 9, QFont.Bold)
        p.setFont(font)
        for i, v in enumerate(self.values):
            span = int(360 * 16 * v / total)
            p.setBrush(QBrush(QColor(PALETTE[i % len(PALETTE)])))
            p.setPen(QPen(QColor("#ffffff"), 2))
            p.drawPie(rect, int(start), span)
            mid_angle = math.radians((start / 16) + (span / 16) / 2)
            lx = rect.center().x() + (size / 2 + 18) * math.cos(mid_angle)
            ly = rect.center().y() - (size / 2 + 18) * math.sin(mid_angle)
            pct = round(100 * v / total)
            p.setPen(QPen(QColor("#333")))
            p.drawText(QPointF(lx - 12, ly), f"{self.labels[i]} ({pct}%)")
            start += span

    def _line(self, p):
        w, h = self.width(), self.height()
        margin = 36
        top = 20
        chart_h = h - margin - top
        vmax = max(self.values) or 1
        vmin = min(self.values)
        n = len(self.values)
        step_x = (w - 2 * margin) / max(1, n - 1)
        pts = []
        for i, v in enumerate(self.values):
            x = margin + i * step_x
            y = h - margin - ((v - vmin) / (vmax - vmin + 1e-9)) * chart_h
            pts.append(QPointF(x, y))
        p.setPen(QPen(QColor("#333"), 2))
        p.drawLine(margin, h - margin, w - margin, h - margin)
        p.setPen(QPen(QColor(PALETTE[0]), 3))
        for i in range(len(pts) - 1):
            p.drawLine(pts[i], pts[i + 1])
        p.setBrush(QBrush(QColor(PALETTE[0])))
        font = QFont("Sans", 8)
        p.setFont(font)
        for i, pt in enumerate(pts):
            p.drawEllipse(pt, 4, 4)
            p.drawText(pt + QPointF(-8, -10), str(self.values[i]))
            p.drawText(QPointF(pt.x() - 8, h - margin + 14), str(self.labels[i]))

    def _box(self, p):
        w, h = self.width(), self.height()
        sv = sorted(self.values)
        n = len(sv)
        lo, hi = sv[0], sv[-1]
        q1 = sv[n // 4]
        med = sv[n // 2] if n % 2 else (sv[n // 2 - 1] + sv[n // 2]) / 2
        q3 = sv[(3 * n) // 4]
        margin = 40
        span = hi - lo or 1
        def X(val):
            return margin + (val - lo) / span * (w - 2 * margin)
        mid_y = h / 2
        p.setPen(QPen(QColor("#333"), 2))
        p.drawLine(X(lo), mid_y, X(q1), mid_y)
        p.drawLine(X(q3), mid_y, X(hi), mid_y)
        p.setBrush(QBrush(QColor(PALETTE[0]).lighter(160)))
        p.drawRect(QRectF(X(q1), mid_y - 30, X(q3) - X(q1), 60))
        p.setPen(QPen(QColor(PALETTE[2]), 3))
        p.drawLine(X(med), mid_y - 30, X(med), mid_y + 30)
        p.setPen(QPen(QColor("#333"), 2))
        for val, label in [(lo, "min"), (q1, "Q1"), (med, "median"), (q3, "Q3"), (hi, "max")]:
            p.drawLine(X(val), mid_y - 36, X(val), mid_y + 36)
            p.drawText(QPointF(X(val) - 14, mid_y + 52), f"{label}\n{val:g}")
