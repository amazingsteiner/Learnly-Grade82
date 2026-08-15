from .base import Screen
from ui.widgets import Card
from engine.paper_engine import PaperEngine


class TutorScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "🔐 Tutor Mode")
        s = app.student
        mastery = s.get("mastery", {})
        avg = sum(mastery.values()) / max(1, len(mastery))

        self.add(Card("👨‍🏫 Tutor Dashboard", f"Current student: {s.get('code','')} • Term {s.get('term',1)}"))
        self.add(Card("📊 Student Analytics",
                      f"Overall mastery: {int(avg*100)}%\n"
                      f"Weaknesses: {', '.join(s.get('weaknesses', [])) or 'None'}\n"
                      f"Strengths: {', '.join(s.get('strengths', [])) or 'None'}\n"
                      f"XP: {s.get('xp',0)} • Streak: {s.get('streak',0)} days"))

        self.add(Card("📝 Generate Weakness Paper", "Create a targeted recovery paper.",
                      ("GENERATE", lambda: self.quick_paper("Weakness Recovery"))))
        self.add(Card("🔥 Generate Strength Paper", "Push the student's strongest topics.",
                      ("GENERATE", lambda: self.quick_paper("Strength Challenge"))))
        self.add(Card("📚 Mock Exam", "Full term-aligned mock exam.",
                      ("GENERATE", lambda: self.quick_paper("Mock Exam"))))

        self.add(Card("🔄 Import / Export", "Timestamp-safe student data transfer.",
                      ("OPEN SETTINGS", app.show_settings)))

        self.finish()

    def quick_paper(self, paper_type):
        pe = PaperEngine(self.app.root)
        paper, path = pe.generate(self.app.student, paper_type=paper_type, count=15)
        self.app.save_student()
        self.app.show_paper_viewer(paper["paper_id"])
