from dataclasses import dataclass, field


@dataclass
class Shape:
    kind: str
    points: list
    label: str = ""
    meta: dict = field(default_factory=dict)


class GeometryEngine:
    """Lightweight shape descriptors. Actual drawing happens in ui/geometry_canvas.py (QPainter)."""

    def triangle(self, a, b, c, label=""):
        return Shape("triangle", [a, b, c], label)

    def right_triangle(self, base, height, label=""):
        return Shape("right_triangle", [(0, 0), (base, 0), (0, height)], label)

    def rectangle(self, x, y, w, h, label=""):
        return Shape("rectangle", [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], label)

    def circle(self, center, radius, label=""):
        return Shape("circle", [center, radius], label)

    def angle(self, vertex, p1, p2, label=""):
        return Shape("angle", [vertex, p1, p2], label)
