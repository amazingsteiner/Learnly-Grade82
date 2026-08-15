import json
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QCheckBox, QSpinBox, QMessageBox, QFileDialog
)
from .base import Screen
from ui.widgets import Card
from ui.theme_manager import THEMES, FONT_SCALES


class SettingsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "⚙ Settings")
        self.settings = app.student.setdefault("settings", {})

        self.add(QLabel("DISPLAY — THEME"))
        self.theme_box = QComboBox()
        self.theme_box.addItems(THEMES.keys())
        self.theme_box.setCurrentText(app.theme.current)
        self.theme_box.currentTextChanged.connect(self.change_theme)
        self.add(self.theme_box)

        self.add(QLabel("DISPLAY — FONT SIZE"))
        self.font_box = QComboBox()
        self.font_box.addItems(FONT_SCALES.keys())
        self.font_box.setCurrentText(self.settings.get("font_scale", "Normal"))
        self.font_box.currentTextChanged.connect(self.change_font)
        self.add(self.font_box)

        self.add(QLabel("LEARNING PREFERENCES"))

        self.hints = QCheckBox("💡 Smart hints during practice")
        self.hints.setChecked(self.settings.get("hints", True))
        self.hints.stateChanged.connect(self.save)
        self.add(self.hints)

        self.sound = QCheckBox("🔊 Sound effects")
        self.sound.setChecked(self.settings.get("sound", True))
        self.sound.stateChanged.connect(self.save)
        self.add(self.sound)

        self.animations = QCheckBox("✨ Animations")
        self.animations.setChecked(self.settings.get("animations", True))
        self.animations.stateChanged.connect(self.save)
        self.add(self.animations)

        self.auto_explain = QCheckBox("📖 Auto-show explanations after answering")
        self.auto_explain.setChecked(self.settings.get("show_solutions", True))
        self.auto_explain.stateChanged.connect(self.save)
        self.add(self.auto_explain)

        self.confirm_reset = QCheckBox("⚠️ Confirm before resetting data")
        self.confirm_reset.setChecked(self.settings.get("confirm_reset", True))
        self.confirm_reset.stateChanged.connect(self.save)
        self.add(self.confirm_reset)

        self.add(QLabel("DIFFICULTY PREFERENCE"))
        self.difficulty_box = QComboBox()
        self.difficulty_box.addItems(["Foundation", "Standard", "Advanced", "Elite"])
        self.difficulty_box.setCurrentText(self.settings.get("difficulty_pref", "Standard"))
        self.difficulty_box.currentTextChanged.connect(self.save)
        self.add(self.difficulty_box)

        self.add(QLabel("DAILY GOAL (problems)"))
        self.goal = QSpinBox()
        self.goal.setRange(5, 100)
        self.goal.setValue(app.student.get("daily_goal", 20))
        self.add(self.goal)

        save_goal = QPushButton("💾 SAVE DAILY GOAL")
        save_goal.clicked.connect(self.save_goal)
        self.add(save_goal)

        self.add(QLabel("DATA"))
        self.add(Card("📤 Export Student Data", "Save a portable JSON backup of your profile.",
                      ("EXPORT", self.export_data)))
        self.add(Card("📥 Import Student Data", "Load a profile export (newer data always wins).",
                      ("IMPORT", self.import_data)))
        self.add(Card("🗑 Reset Local Data", "Clear today's progress and history for this profile.",
                      ("RESET", self.reset_data)))

        self.add(QLabel("ABOUT"))
        self.add(Card("Learnly — Grade 8 Mathematics",
                      "CAPS-aligned. Adaptive local logic, no online AI required.\n"
                      "Curriculum content should be verified against the current DBE ATP before formal school use."))

        tutor = QPushButton("🔐 TUTOR MODE")
        tutor.clicked.connect(app.show_tutor_gate)
        self.add(tutor)

        self.finish()

    def save(self):
        self.settings["hints"] = self.hints.isChecked()
        self.settings["sound"] = self.sound.isChecked()
        self.settings["animations"] = self.animations.isChecked()
        self.settings["show_solutions"] = self.auto_explain.isChecked()
        self.settings["confirm_reset"] = self.confirm_reset.isChecked()
        self.settings["difficulty_pref"] = self.difficulty_box.currentText()
        self.app.save_student()

    def change_theme(self, name):
        self.app.theme.set_theme(name)
        self.settings["theme"] = name
        self.app.save_student()

    def change_font(self, name):
        self.app.theme.set_font_scale(name)
        self.settings["font_scale"] = name
        self.app.save_student()
        self.app.refresh_current_screen()

    def save_goal(self):
        self.app.student["daily_goal"] = self.goal.value()
        self.app.save_student()
        QMessageBox.information(self, "Saved", "Daily goal updated.")

    def export_data(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = self.app.root / "data" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        path = export_dir / f"{self.app.student['code']}_{stamp}.json"
        path.write_text(json.dumps({
            "format": "learnly_grade8_export_v1",
            "exported_at": datetime.now().isoformat(),
            "student": self.app.student
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        QMessageBox.information(self, "Export complete", str(path))

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Student Data", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            incoming = data.get("student", data)
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))
            return

        current_updated = self.app.student.get("updated_at", "")
        incoming_updated = incoming.get("updated_at", "")
        if incoming_updated and incoming_updated <= current_updated:
            QMessageBox.warning(self, "Import Skipped",
                "The imported profile is older than or the same age as your current data. "
                "Nothing was overwritten to protect your newer progress.")
            return

        self.app.student.update(incoming)
        self.app.save_student()
        QMessageBox.information(self, "Import Complete", "Newer student data imported successfully.")
        self.app.show_settings()

    def reset_data(self):
        if self.confirm_reset.isChecked():
            reply = QMessageBox.question(self, "Confirm Reset",
                "This will reset today's progress and streak. Mastery history is kept. Continue?")
            if reply != QMessageBox.Yes:
                return
        self.app.student["today_done"] = 0
        self.app.student["streak"] = 0
        self.app.save_student()
        QMessageBox.information(self, "Reset Complete", "Today's progress has been reset.")
