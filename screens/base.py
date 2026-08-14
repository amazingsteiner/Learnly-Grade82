from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea

class Screen(QWidget):
    def __init__(self, app, title):
        super().__init__()
        self.app = app
        outer = QVBoxLayout(self)
        top = QHBoxLayout()
        back = QPushButton("←")
        back.clicked.connect(app.show_home)
        top.addWidget(back)
        label = QLabel(title)
        label.setStyleSheet("font-size: 18pt; font-weight: 800;")
        top.addWidget(label)
        top.addStretch()
        outer.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(8, 8, 8, 8)
        scroll.setWidget(self.content)
        outer.addWidget(scroll)

    def add(self, widget):
        self.body.addWidget(widget)

    def finish(self):
        self.body.addStretch()
