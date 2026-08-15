import random
from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit, QHBoxLayout
from .base import Screen
from engine.timer_engine import Stopwatch
from engine.answer_check import answers_match

TRICKS = [
    {"skill": "×25 shortcut", "gen": lambda: (lambda a: (f"{a} × 25", a*25, "×25 = ×100 ÷ 4"))(random.randint(4, 80))},
    {"skill": "×9 shortcut", "gen": lambda: (lambda a: (f"{a} × 9", a*9, "×9 = ×10 − the original number"))(random.randint(2, 90))},
    {"skill": "×5 shortcut", "gen": lambda: (lambda a: (f"{a} × 5", a*5, "×5 = ×10 ÷ 2"))(random.randint(2, 200))},
    {"skill": "10% of a number", "gen": lambda: (lambda a: (f"10% of {a}", round(a*0.1,2), "10% = divide by 10"))(random.randint(10, 900))},
    {"skill": "Same-base exponents", "gen": lambda: (lambda a,x,y: (f"{a}^{x} × {a}^{y}", f"{a}^{x+y}", "Add the exponents"))(random.randint(2,5), random.randint(1,4), random.randint(1,4))},
    {"skill": "Doubling & halving", "gen": lambda: (lambda a: (f"{a} × 50", a*50, "×50 = ×100 ÷ 2"))(random.randint(2, 60))},
    {"skill": "Percentages", "gen": lambda: (lambda a: (f"25% of {a}", round(a*0.25,2), "25% = ÷4"))(random.randint(8, 400))},
]


class MentalMathsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "🧮 Mental Maths")
        self.streak = 0
        self.best = app.student.get("mental_best_streak", 0)
        self.current = None
        self.sw = Stopwatch(self)
        self.sw.tick.connect(self.on_tick)

        self.streak_label = QLabel()
        self.add(self.streak_label)

        self.skill_label = QLabel()
        self.skill_label.setProperty("ui_role", "muted")
        self.add(self.skill_label)

        self.question = QLabel()
        self.question.setStyleSheet("font-size: 20pt; font-weight: 800;")
        self.add(self.question)

        self.tip_label = QLabel()
        self.tip_label.setWordWrap(True)
        self.add(self.tip_label)

        self.answer = QLineEdit()
        self.answer.setPlaceholderText("Fast answer")
        self.answer.returnPressed.connect(self.check)
        self.add(self.answer)

        row = QHBoxLayout()
        check = QPushButton("CHECK")
        check.clicked.connect(self.check)
        row.addWidget(check)
        skip = QPushButton("SKIP")
        skip.setProperty("ui_role", "secondary")
        skip.clicked.connect(self.next_q)
        row.addWidget(skip)
        self.add_layout(row)

        self.result = QLabel()
        self.result.setWordWrap(True)
        self.add(self.result)

        self.time_label = QLabel()
        self.time_label.setProperty("ui_role", "muted")
        self.add(self.time_label)

        self.finish()
        self.next_q()
        self.sw.start()

    def on_tick(self, seconds):
        self.time_label.setText(f"⏱ {seconds}s")

    def update_streak_label(self):
        self.streak_label.setText(f"🔥 Streak: {self.streak}   🏆 Best: {self.best}")

    def next_q(self):
        trick = random.choice(TRICKS)
        q, a, tip = trick["gen"]()
        self.current = (q, str(a), tip, trick["skill"])
        self.skill_label.setText(f"Skill: {trick['skill']}")
        self.question.setText(q + " = ?")
        self.tip_label.clear()
        self.answer.clear()
        self.result.clear()
        self.update_streak_label()

    def check(self):
        if not self.current:
            return
        q, expected, tip, skill = self.current
        user = self.answer.text().strip()
        correct = answers_match(user, expected)
        if correct:
            self.streak += 1
            self.best = max(self.best, self.streak)
            self.app.student["mental_best_streak"] = self.best
            self.app.student["xp"] = self.app.student.get("xp", 0) + 5
            self.result.setText(f"✓ Correct! Fast method: {tip}")
        else:
            self.streak = 0
            self.result.setText(f"✗ Answer: {expected}\nFast method: {tip}")
        self.app.save_student()
        self.update_streak_label()
        self.next_q()
