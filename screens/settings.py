from .base import Screen
from ui.widgets import Card
from ui.theme_manager import THEMES
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QCheckBox, QMessageBox
import json
from pathlib import Path

class SettingsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Settings")
        self.add(QLabel("THEME"))
        self.combo = QComboBox()
        self.combo.addItems(THEMES.keys())
        self.combo.setCurrentText(app.theme.current)
        self.combo.currentTextChanged.connect(self.change_theme)
        self.add(self.combo)

        self.hints = QCheckBox("Smart hints")
        self.hints.setChecked(app.student.get("settings", {}).get("hints", True))
        self.hints.stateChanged.connect(self.save)
        self.add(self.hints)

        self.add(Card("🎯 Daily Goal", "Daily problem target is stored per student."))

        tutor = QPushButton("🔐 TUTOR MODE")
        tutor.clicked.connect(self.tutor)
        self.add(tutor)
        self.finish()

    def save(self):
        self.app.student.setdefault("settings", {})["hints"] = self.hints.isChecked()
        self.persist()

    def change_theme(self, name):
        self.app.theme.set_theme(name)
        self.app.student.setdefault("settings", {})["theme"] = name
        self.persist()

    def persist(self):
        path = Path(__file__).resolve().parents[1] / "data" / "students" / f"{self.app.student['code']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.app.student, indent=2), encoding="utf-8")

    def tutor(self):
        from PySide6.QtWidgets import QInputDialog
        code, ok = QInputDialog.getText(self, "Tutor Access", "Access code:")
        if ok and code.strip().lower() == "children of the sun":
            self.app.show_tutor()
        else:
            QMessageBox.warning(self, "Access denied", "Incorrect access code.")
