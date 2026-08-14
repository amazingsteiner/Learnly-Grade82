from .base import Screen
from ui.widgets import Card, BottomNav

class PracticeScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Practice")
        modes = [
            ("🎯 Daily Practice", "Work toward today's problem goal."),
            ("🤖 Recommended", "Practice selected from your current mastery."),
            ("🔴 Weakness Recovery", "Target your weakest topics."),
            ("🔥 Strength Challenge", "Push topics where you already perform well."),
            ("🔄 Mixed Practice", "Mix topics for broader retention."),
            ("⚡ Speed Challenge", "Timed questions and personal bests."),
            ("🧠 Mental Maths", "Fast calculation, tricks and shortcuts.")
        ]
        for title, body in modes:
            self.add(Card(title, body, ("START", lambda m=title: self.start(m))))
        self.add(BottomNav(app))
        self.finish()

    def start(self, mode):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Practice", f"{mode}\\n\\nPractice engine module ready to connect.")
