from .base import Screen
from ui.widgets import Card, BottomNav

class LearnScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Learn")
        for topic, mastery in app.student.get("mastery", {}).items():
            self.add(Card(topic, f"Mastery: {int(mastery*100)}% • Guide • Techniques • Examples",
                          ("OPEN TOPIC", lambda t=topic: self.topic(t))))
        self.add(BottomNav(app))
        self.finish()

    def topic(self, topic):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, topic,
            f"{topic}\\n\\nFuture module: step-by-step guide, worked examples, "
            "shortcuts, common mistakes, visualisation and adaptive practice."
        )
