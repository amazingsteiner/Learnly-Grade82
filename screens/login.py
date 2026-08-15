from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt


class LoginScreen(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 60, 30, 30)
        layout.setSpacing(12)
        layout.addStretch()

        title = QLabel("Learnly")
        title.setStyleSheet("font-size: 32pt; font-weight: 800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Grade 8 Mathematics • The Elites Academy")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        label = QLabel("STUDENT CODE")
        label.setStyleSheet("font-weight: 700;")
        layout.addWidget(label)

        self.code = QLineEdit()
        self.code.setPlaceholderText("Example: S01")
        self.code.setMinimumHeight(46)
        self.code.returnPressed.connect(self.login)
        layout.addWidget(self.code)

        login_button = QPushButton("ENTER LEARNLY")
        login_button.setMinimumHeight(48)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        info = QLabel(
            "Enter your student code to continue.\n"
            "If this is your first time, Learnly will automatically "
            "create your Grade 8 profile."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()

    def login(self):
        code = self.code.text().strip().upper()
        if not code:
            QMessageBox.warning(self, "Student Code Required", "Please enter your student code.")
            return
        if len(code) < 2:
            QMessageBox.warning(self, "Invalid Student Code", "Please enter a valid student code.")
            return
        self.callback(code)
