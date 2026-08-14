from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame

class LoginScreen(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 70, 30, 30)

        title = QLabel("Learnly")
        title.setStyleSheet("font-size: 30pt; font-weight: 800;")
        layout.addWidget(title)

        subtitle = QLabel("Learn smarter. Master more.")
        layout.addWidget(subtitle)

        layout.addSpacing(45)
        layout.addWidget(QLabel("STUDENT CODE"))
        self.code = QLineEdit()
        self.code.setPlaceholderText("Enter your student code")
        self.code.returnPressed.connect(self.login)
        layout.addWidget(self.code)

        login = QPushButton("LOGIN")
        login.clicked.connect(self.login)
        layout.addWidget(login)
        layout.addStretch()

    def login(self):
        self.callback(self.code.text())
