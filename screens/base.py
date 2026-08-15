from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt


class Screen(QWidget):
    def __init__(self, app, title, show_back=True):
        super().__init__()
        self.app = app

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 10)
        outer.setSpacing(8)

        if show_back:
            top = QHBoxLayout()
            back = QPushButton("←")
            back.setProperty("ui_role", "secondary")
            back.setFixedWidth(46)
            back.clicked.connect(app.show_home)
            top.addWidget(back)

            label = QLabel(title)
            label.setProperty("ui_role", "title")
            label.setWordWrap(True)
            top.addWidget(label, 1)
            outer.addLayout(top)
        else:
            label = QLabel(title)
            label.setProperty("ui_role", "title")
            outer.addWidget(label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content = QWidget()
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(2, 2, 2, 2)
        self.body.setSpacing(10)

        scroll.setWidget(self.content)
        outer.addWidget(scroll, 1)

    def add(self, widget):
        self.body.addWidget(widget)

    def add_layout(self, layout):
        self.body.addLayout(layout)

    def finish(self):
        self.body.addStretch()
