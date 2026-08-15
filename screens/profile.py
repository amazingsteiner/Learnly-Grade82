from .base import Screen
from ui.widgets import Card, BottomNav, MasteryBar
from PySide6.QtWidgets import QLabel


class ProfileScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "👤 Profile")
        s = app.student
        mastery = s.get("mastery", {})
        avg = sum(mastery.values()) / max(1, len(mastery))

        self.add(Card(s.get("name", "Student"),
                      f"Student code: {s.get('code','')}\nGrade 8 Mathematics • Term {s.get('term',1)}"))
        self.add(Card("🏆 Elite Level", f"Level {s.get('level',1)} • {s.get('xp',0)} XP"))
        self.add(Card("📊 Overall Mastery", f"{int(avg*100)}%"))
        self.add(Card("🎯 Daily Goal",
                      f"{s.get('today_done',0)} / {s.get('daily_goal',20)} • 🔥 {s.get('streak',0)} day streak"))

        self.add(QLabel("MASTERY BY TOPIC"))
        for topic, val in sorted(mastery.items(), key=lambda x: -x[1]):
            self.add(MasteryBar(topic.replace("_", " ").title(), val))

        weak = s.get("weaknesses", [])
        strong = s.get("strengths", [])
        self.add(Card("🔴 Weaknesses", ", ".join(w.replace("_"," ").title() for w in weak) or "None yet"))
        self.add(Card("🟢 Strengths", ", ".join(w.replace("_"," ").title() for w in strong) or "None yet"))

        self.add(Card("⚙ Settings", "Theme, display size and preferences.",
                      ("OPEN SETTINGS", app.show_settings)))
        self.add(Card("🔐 Tutor Mode", "Access code required.",
                      ("ENTER TUTOR MODE", app.show_tutor_gate)))

        self.add(BottomNav(app))
        self.finish()
