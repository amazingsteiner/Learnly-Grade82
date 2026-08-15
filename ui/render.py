import math
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap

PALETTE = ["#3157D5", "#159A68", "#D64545", "#F5A623", "#8B5CF6", "#06B6D4", "#EC4899"]


def _new_pixmap(w, h, bg="#ffffff"):
    pm = QPixmap(w, h)
    pm.fill(QColor(bg))
    return pm


def diagram_to_pixmap(diagram, w=320, h=240):
    """Renders a question 'diagram' dict (from QuestionEngine) to a static image."""
    pm = _new_pixmap(w, h)
    if not diagram:
        return pm
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    d = diagram
    kind = d.get("type")
    pen = QPen(QColor("#3157D5"), 3)
    p.setPen(pen)
    p.setFont(QFont("Sans", 11, QFont.Bold))

    if kind == "right_triangle":
        margin = 40
        base = min(w, h) - 2 * margin
        x0, y0 = margin, h - margin
        p.drawLine(QPointF(x0, y0), QPointF(x0 + base, y0))
        p.drawLine(QPointF(x0, y0), QPointF(x0, y0 - base * 0.75))
        p.drawLine(QPointF(x0 + base, y0), QPointF(x0, y0 - base * 0.75))
        p.drawRect(QRectF(x0, y0 - 14, 14, 14))
        a = d.get("a", "?"); b = d.get("b", "?"); c = d.get("c", "?")
        find = d.get("find")
        if "a" in d:
            p.drawText(QPointF(x0 + base / 2 - 10, y0 + 22), f"{a if find!='a' else '?'} cm")
        if "b" in d:
            p.drawText(QPointF(x0 - 34, y0 - base * 0.35), f"{b if find!='b' else '?'} cm")
        if "c" in d:
            p.drawText(QPointF(x0 + base / 2 - 10, y0 - base * 0.45), f"{c if find!='c' else '?'} cm")

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
        for ang in [0, 100, 220]:
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
        _draw_grid(p, w, h)
        scale = min(w, h) / 22
        cx, cy = w / 2, h / 2
        x, y = d.get("x", 0), d.get("y", 0)
        p1 = QPointF(cx + x * scale, cy - y * scale)
        p.setBrush(QBrush(QColor("#3157D5")))
        p.setPen(pen)
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

    p.end()
    return pm


def _draw_grid(p, w, h):
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


def chart_to_pixmap(values, labels=None, mode="bar", w=320, h=260):
    pm = _new_pixmap(w, h)
    if not values:
        p = QPainter(pm)
        p.drawText(pm.rect(), Qt.AlignCenter, "No data yet")
        p.end()
        return pm
    labels = labels or [str(i + 1) for i in range(len(values))]
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    if mode == "bar":
        _bar(p, values, labels, w, h)
    elif mode == "pie":
        _pie(p, values, labels, w, h)
    elif mode == "line":
        _line(p, values, labels, w, h)
    elif mode == "box":
        _box(p, values, w, h)
    elif mode == "histogram":
        _histogram(p, values, w, h)
    p.end()
    return pm


def _bar(p, values, labels, w, h):
    margin, top = 36, 20
    chart_h = h - margin - top
    vmax = max(values) or 1
    n = len(values)
    bw = (w - 2 * margin) / max(1, n)
    p.setFont(QFont("Sans", 9))
    for i, v in enumerate(values):
        bar_h = (v / vmax) * chart_h
        x = margin + i * bw + bw * 0.15
        y = h - margin - bar_h
        p.setBrush(QBrush(QColor(PALETTE[i % len(PALETTE)])))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(x, y, bw * 0.7, bar_h))
        p.setPen(QPen(QColor("#333")))
        p.drawText(QRectF(x - 5, h - margin + 4, bw, 16), Qt.AlignCenter, str(labels[i]))
        p.drawText(QRectF(x - 5, y - 16, bw + 10, 14), Qt.AlignCenter, str(v))
    p.setPen(QPen(QColor("#333"), 2))
    p.drawLine(margin, h - margin, w - margin, h - margin)


def _pie(p, values, labels, w, h):
    size = min(w, h) - 70
    rect = QRectF((w - size) / 2, (h - size) / 2 - 10, size, size)
    total = sum(values) or 1
    start = 0
    p.setFont(QFont("Sans", 9, QFont.Bold))
    for i, v in enumerate(values):
        span = int(360 * 16 * v / total)
        p.setBrush(QBrush(QColor(PALETTE[i % len(PALETTE)])))
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.drawPie(rect, int(start), span)
        mid_angle = math.radians((start / 16) + (span / 16) / 2)
        lx = rect.center().x() + (size / 2 + 18) * math.cos(mid_angle)
        ly = rect.center().y() - (size / 2 + 18) * math.sin(mid_angle)
        pct = round(100 * v / total)
        p.setPen(QPen(QColor("#333")))
        p.drawText(QPointF(lx - 12, ly), f"{labels[i]} ({pct}%)")
        start += span


def _line(p, values, labels, w, h):
    margin, top = 36, 20
    chart_h = h - margin - top
    vmax, vmin = max(values) or 1, min(values)
    n = len(values)
    step_x = (w - 2 * margin) / max(1, n - 1)
    pts = []
    for i, v in enumerate(values):
        x = margin + i * step_x
        y = h - margin - ((v - vmin) / (vmax - vmin + 1e-9)) * chart_h
        pts.append(QPointF(x, y))
    p.setPen(QPen(QColor("#333"), 2))
    p.drawLine(margin, h - margin, w - margin, h - margin)
    p.setPen(QPen(QColor(PALETTE[0]), 3))
    for i in range(len(pts) - 1):
        p.drawLine(pts[i], pts[i + 1])
    p.setBrush(QBrush(QColor(PALETTE[0])))
    p.setFont(QFont("Sans", 8))
    for i, pt in enumerate(pts):
        p.drawEllipse(pt, 4, 4)
        p.drawText(pt + QPointF(-8, -10), str(values[i]))
        p.drawText(QPointF(pt.x() - 8, h - margin + 14), str(labels[i]))


def _box(p, values, w, h):
    sv = sorted(values)
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


def _histogram(p, values, w, h):
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    n_bins = min(8, max(4, len(values) // 2))
    bin_w = span / n_bins
    bins = [0] * n_bins
    for v in values:
        idx = min(n_bins - 1, int((v - lo) / bin_w)) if bin_w else 0
        bins[idx] += 1
    labels = [f"{lo+i*bin_w:.0f}-{lo+(i+1)*bin_w:.0f}" for i in range(n_bins)]
    _bar(p, bins, labels, w, h)


def science_diagram_to_pixmap(kind, w=320, h=240):
    """Code-generated science diagrams (no external image assets/copyright risk)."""
    pm = _new_pixmap(w, h)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setFont(QFont("Sans", 10, QFont.Bold))

    if kind == "states_of_matter":
        labels = ["Solid", "Liquid", "Gas"]
        for i, label in enumerate(labels):
            cx = w / 6 + i * w / 3
            cy = h / 2
            box = QRectF(cx - w / 8, 20, w / 4, h - 60)
            p.setPen(QPen(QColor("#333"), 1))
            p.drawRect(box)
            p.setBrush(QBrush(QColor("#3157D5")))
            p.setPen(Qt.NoPen)
            import random as _r
            _r.seed(i)
            if label == "Solid":
                for row in range(4):
                    for col in range(3):
                        px = box.left() + 10 + col * (box.width() - 20) / 2
                        py = box.top() + 15 + row * (box.height() - 30) / 3
                        p.drawEllipse(QPointF(px, py), 5, 5)
            elif label == "Liquid":
                for _ in range(12):
                    px = box.left() + _r.uniform(8, box.width() - 8)
                    py = box.top() + box.height() * 0.4 + _r.uniform(0, box.height() * 0.55)
                    p.drawEllipse(QPointF(px, py), 5, 5)
            else:
                for _ in range(10):
                    px = box.left() + _r.uniform(8, box.width() - 8)
                    py = box.top() + _r.uniform(8, box.height() - 8)
                    p.drawEllipse(QPointF(px, py), 4, 4)
            p.setPen(QPen(QColor("#333")))
            p.drawText(QRectF(box.left(), box.bottom() + 6, box.width(), 20), Qt.AlignCenter, label)

    elif kind == "water_cycle":
        p.setPen(QPen(QColor("#3157D5"), 2))
        # sun
        p.setBrush(QBrush(QColor("#F5A623")))
        p.drawEllipse(QPointF(w * 0.8, h * 0.18), 20, 20)
        # sea
        p.setBrush(QBrush(QColor("#89CFF0")))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(0, h * 0.75, w, h * 0.25))
        # cloud
        p.setBrush(QBrush(QColor("#e0e0e0")))
        p.drawEllipse(QPointF(w * 0.35, h * 0.22), 30, 18)
        p.drawEllipse(QPointF(w * 0.48, h * 0.2), 24, 16)
        # arrows: evaporation, condensation, precipitation
        p.setPen(QPen(QColor("#333"), 2))
        p.drawLine(QPointF(w * 0.25, h * 0.75), QPointF(w * 0.32, h * 0.3))
        p.drawLine(QPointF(w * 0.45, h * 0.32), QPointF(w * 0.4, h * 0.7))
        p.setFont(QFont("Sans", 8))
        p.drawText(QPointF(w * 0.05, h * 0.55), "Evaporation")
        p.drawText(QPointF(w * 0.5, h * 0.55), "Precipitation")
        p.drawText(QPointF(w * 0.25, h * 0.12), "Condensation")

    elif kind == "food_chain":
        items = ["Sun", "Grass", "Grasshopper", "Frog", "Snake"]
        seg = w / len(items)
        p.setPen(QPen(QColor("#333"), 2))
        p.setFont(QFont("Sans", 8, QFont.Bold))
        for i, item in enumerate(items):
            cx = seg * i + seg / 2
            cy = h / 2
            p.setBrush(QBrush(QColor(PALETTE[i % len(PALETTE)])))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(cx, cy), 28, 28)
            p.setPen(QPen(QColor("#fff")))
            p.drawText(QRectF(cx - 28, cy - 10, 56, 20), Qt.AlignCenter, item)
            if i < len(items) - 1:
                p.setPen(QPen(QColor("#333"), 2))
                p.drawLine(QPointF(cx + 28, cy), QPointF(cx + seg - 28, cy))

    elif kind == "simple_circuit":
        p.setPen(QPen(QColor("#333"), 3))
        rect = QRectF(40, 40, w - 80, h - 100)
        p.drawRect(rect)
        # battery symbol
        p.drawLine(QPointF(rect.left(), rect.top() + rect.height() / 2 - 10),
                   QPointF(rect.left(), rect.top() + rect.height() / 2 + 10))
        p.setFont(QFont("Sans", 9))
        p.drawText(QPointF(rect.left() - 30, rect.top() + rect.height() / 2 + 30), "Battery")
        # bulb
        p.setBrush(QBrush(QColor("#F5A623")))
        p.drawEllipse(QPointF(rect.right(), rect.top() + rect.height() / 2), 14, 14)
        p.drawText(QPointF(rect.right() - 15, rect.top() + rect.height() / 2 + 32), "Bulb")

    p.end()
    return pm
