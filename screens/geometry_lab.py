from PySide6.QtWidgets import QLabel, QComboBox, QPushButton, QHBoxLayout, QCheckBox
from .base import Screen
from ui.geometry_canvas import GeometryLabCanvas


class GeometryLabScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "📐 Geometry Drawer")

        sub = QLabel("Tap points on the grid to build a shape. No manual images needed — "
                     "every diagram is drawn live.")
        sub.setProperty("ui_role", "subtitle")
        sub.setWordWrap(True)
        self.add(sub)

        self.selector = QComboBox()
        self.selector.addItems(GeometryLabCanvas.MODES)
        self.selector.setCurrentText("Triangle")
        self.selector.currentTextChanged.connect(self.change_mode)
        self.add(self.selector)

        self.canvas = GeometryLabCanvas()
        self.add(self.canvas)

        self.measure_box = QCheckBox("📏 Show measurements")
        self.measure_box.setChecked(True)
        self.measure_box.stateChanged.connect(self.toggle_measure)
        self.add(self.measure_box)

        row = QHBoxLayout()
        clear = QPushButton("🗑 CLEAR")
        clear.setProperty("ui_role", "secondary")
        clear.clicked.connect(self.canvas.clear)
        row.addWidget(clear)
        self.add_layout(row)

        tip = QLabel(
            "TIP: Triangle needs 3 taps, Rectangle & Circle need 2 taps (opposite corners / "
            "centre + edge), Angle needs 3 taps (vertex first), Coordinate Plane plots every tap."
        )
        tip.setProperty("ui_role", "muted")
        tip.setWordWrap(True)
        self.add(tip)

        self.finish()

    def change_mode(self, mode):
        self.canvas.mode = mode
        self.canvas.clear()

    def toggle_measure(self, state):
        self.canvas.show_measurements = bool(state)
        self.canvas.update()
