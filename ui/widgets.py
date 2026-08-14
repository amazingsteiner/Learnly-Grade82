from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget

class Card(QFrame):
    def __init__(self, title, body="", action=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13pt; font-weight: 700;")
        layout.addWidget(title_label)
        if body:
            body_label = QLabel(body)
            body_label.setWordWrap(True)
            layout.addWidget(body_label)
        if action:
            button = QPushButton(action[0])
            button.clicked.connect(action[1])
            layout.addWidget(button)

class BottomNav(QWidget):
    def __init__(self, app):
        super().__init__()
        layout = QHBoxLayout(self)
        buttons = [
            ("Home", app.show_home), ("Learn", app.show_learn),
            ("Practice", app.show_practice), ("Papers", app.show_papers),
            ("Profile", app.show_profile)
        ]
        for text, callback in buttons:
            b = QPushButton(text)
            b.clicked.connect(callback)
            layout.addWidget(b)
