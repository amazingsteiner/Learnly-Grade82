from .base import Screen
from ui.widgets import Card

class TutorScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Tutor Mode")
        s = app.student
        self.add(Card("👨‍🏫 Tutor Dashboard",
                      f"Current student: {s.get('code','')}"))
        self.add(Card("📊 Student Analytics",
                      "Future module: mastery, accuracy, speed, mistakes and trends."))
        self.add(Card("📝 Assessment Builder",
                      "Future module: personalised term-aware papers."))
        self.add(Card("🔄 Import / Export",
                      "Future module: timestamp-safe student data transfer."))
        self.add(Card("🎯 Assign Practice",
                      "Future module: tutor-selected practice sessions."))
        self.finish()
