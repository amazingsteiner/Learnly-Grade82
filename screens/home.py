from .base import Screen
from ui.widgets import Card, BottomNav

class HomeScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Learnly")
        s = app.student
        goal = s.get("daily_goal", 20)
        done = s.get("today_done", 0)
        weak = sorted(s.get("mastery", {}), key=s.get("mastery", {}).get)[:2]

        self.add(Card(
            f"Welcome, {s.get('name','Student')}",
            f"Grade {s.get('grade',11)} Mathematics • Term {s.get('term',3)}"
        ))
        self.add(Card(
            "🎯 Today's Goal",
            f"{done} / {goal} problems • {max(goal-done,0)} remaining • 🔥 {s.get('streak',0)} day streak"
        ))
        self.add(Card(
            "🤖 Learnly Guide",
            f"Recommended focus: {', '.join(weak) if weak else 'mixed practice'}.",
            ("START RECOMMENDED PRACTICE", app.show_practice)
        ))
        self.add(Card("📚 Continue Learning",
                      "Continue your current topic and review techniques.",
                      ("OPEN LEARN", app.show_learn)))
        self.add(Card("✏ Practice",
                      "Daily, weakness, strength, mixed, speed and mental maths.",
                      ("PRACTICE", app.show_practice)))
        self.add(Card("📝 Question Papers",
                      "Generate, view and export personalised papers.",
                      ("OPEN PAPERS", app.show_papers)))
        self.add(BottomNav(app))
        self.finish()
