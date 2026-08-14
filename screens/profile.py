from .base import Screen
from ui.widgets import Card, BottomNav
from PySide6.QtWidgets import QPushButton

class ProfileScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Profile")
        s = app.student
        avg = sum(s.get("mastery", {}).values()) / max(1, len(s.get("mastery", {})))
        self.add(Card(s.get("name","Student"),
                      f"Student code: {s.get('code','')}\\nGrade {s.get('grade',11)} Mathematics"))
        self.add(Card("🏆 Elite Level", f"Level {min(10, 1+s.get('xp',0)//100)} • {s.get('xp',0)} XP"))
        self.add(Card("📊 Overall Mastery", f"{int(avg*100)}%"))
        self.add(Card("🎯 Daily Goal",
                      f"{s.get('today_done',0)} / {s.get('daily_goal',20)} • 🔥 {s.get('streak',0)} day streak"))
        self.add(Card("⚙ Settings", "Themes, hints and learning preferences.",
                      ("OPEN SETTINGS", app.show_settings)))
        self.add(BottomNav(app))
        self.finish()
