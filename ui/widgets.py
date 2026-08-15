from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt


class Card(QFrame):
    def __init__(self, title, body="", action=None, secondary_action=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setProperty("ui_role", "heading")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if body:
            body_label = QLabel(body)
            body_label.setWordWrap(True)
            body_label.setProperty("ui_role", "subtitle")
            layout.addWidget(body_label)

        if action or secondary_action:
            row = QHBoxLayout()
            if action:
                b = QPushButton(action[0])
                b.clicked.connect(action[1])
                row.addWidget(b)
            if secondary_action:
                b2 = QPushButton(secondary_action[0])
                b2.setProperty("ui_role", "secondary")
                b2.clicked.connect(secondary_action[1])
                row.addWidget(b2)
            layout.addLayout(row)


class TopicTile(QFrame):
    """Compact topic tile for Learn / Choose Topic screens."""
    def __init__(self, icon, name, subtitle, on_open, on_practice=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        top = QHBoxLayout()
        title = QLabel(f"{icon}  {name}")
        title.setProperty("ui_role", "heading")
        title.setWordWrap(True)
        top.addWidget(title)
        layout.addLayout(top)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setProperty("ui_role", "subtitle")
            sub.setWordWrap(True)
            layout.addWidget(sub)

        row = QHBoxLayout()
        open_btn = QPushButton("OPEN NOTES")
        open_btn.clicked.connect(on_open)
        row.addWidget(open_btn)

        if on_practice:
            prac_btn = QPushButton("PRACTICE THIS")
            prac_btn.setProperty("ui_role", "secondary")
            prac_btn.clicked.connect(on_practice)
            row.addWidget(prac_btn)

        layout.addLayout(row)


class BottomNav(QWidget):
    def __init__(self, app):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)
        buttons = [
            ("🏠", app.show_home), ("📚", app.show_learn),
            ("✏️", app.show_practice), ("📝", app.show_papers),
            ("👤", app.show_profile)
        ]
        for text, callback in buttons:
            b = QPushButton(text)
            b.setProperty("ui_role", "secondary")
            b.setFixedHeight(44)
            b.clicked.connect(callback)
            layout.addWidget(b)


class MasteryBar(QWidget):
    """Small horizontal mastery indicator with label."""
    def __init__(self, label, value, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        lbl = QLabel(label)
        lbl.setMinimumWidth(150)
        layout.addWidget(lbl)

        from PySide6.QtWidgets import QProgressBar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(value * 100))
        bar.setFormat(f"{int(value*100)}%")
        layout.addWidget(bar)
