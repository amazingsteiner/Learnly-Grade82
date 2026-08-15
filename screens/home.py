from .base import Screen
from ui.widgets import Card, BottomNav
from engine.adaptive import AdaptiveEngine


class HomeScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Learnly", show_back=False)
        s = app.student
        goal = s.get("daily_goal", 20)
        done = s.get("today_done", 0)
        ad = AdaptiveEngine(s)
        rec = ad.recommendation_text()

        self.add(Card(
            f"Welcome, {s.get('name','Student')} 👋",
            f"Grade 8 Mathematics • Term {s.get('term',1)} • CAPS"
        ))

        self.add(Card(
            "🎯 Today's Goal",
            f"{done} / {goal} problems • {max(goal-done,0)} remaining • 🔥 {s.get('streak',0)} day streak"
        ))

        self.add(Card(
            "🤖 Learnly Guide",
            rec,
            ("START RECOMMENDED PRACTICE", lambda: app.show_practice(mode="recommended"))
        ))

        self.add(Card("📚 Learn",
                      "Deep notes, worked examples, guides and shortcuts for every Grade 8 topic.",
                      ("OPEN LEARN", app.show_learn)))

        self.add(Card("🔬 Natural Sciences",
                      "Matter & Materials, Life & Living, Energy & Change, Planet Earth & Beyond.",
                      ("OPEN NATURAL SCIENCES", app.show_science)))

        self.add(Card("🧠 Definitions Quiz",
                      "Multiple-choice quiz on key terms from Maths or Natural Sciences.",
                      ("START QUIZ", app.show_quiz)))

        self.add(Card("✏️ Practice",
                      "Choose a topic, difficulty and question count — or let Learnly recommend one.",
                      ("PRACTICE", lambda: app.show_practice())))

        self.add(Card("📝 Question Papers",
                      "Generate term-aligned, weakness or strength papers with a memo.",
                      ("OPEN PAPERS", app.show_papers)))

        self.add(Card("📐 Maths Labs",
                      "Geometry drawer, Data Handling lab and Probability simulator.",
                      ("OPEN LABS", app.show_labs)))

        self.add(Card("🧮 Mental Maths",
                      "Fast calculation tricks with a timer and streak tracking.",
                      ("START", app.show_mental)))

        self.add(BottomNav(app))
        self.finish()
