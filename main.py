import sys
from PySide6.QtWidgets import QApplication
from engine.app import LearnlyApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LearnlyApp()
    window.show()
    sys.exit(app.exec())
