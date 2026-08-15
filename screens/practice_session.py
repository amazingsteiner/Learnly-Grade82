import random
from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit, QProgressBar, QHBoxLayout
from PySide6.QtCore import Qt
from .base import Screen
from ui.render import diagram_to_pixmap
from engine.question_engine import QuestionEngine
from engine.adaptive import AdaptiveEngine
from engine.mastery import MasteryEngine
from engine.timer_engine import CountdownTimer
from engine.answer_check import answers_match


class PracticeSessionScreen(Screen):
    def __init__(self, app, mode="recommended", topics=None, difficulty=2,
                 count=10, timed=False, hints=True, show_solution=True):
        super().__init__(app, "Practice Session")
        self.mode = mode
        self.topics = topics or []
        self.base_difficulty = difficulty
        self.total = count
        self.timed = timed
        self.show_hints = hints
        self.show_solution = show_solution
        self.answered = 0
        self.correct_count = 0
        self.q = None

        self.qe = QuestionEngine()
        self.ad = AdaptiveEngine(app.student)
        self.me = MasteryEngine(app.student)

        self.progress = QProgressBar()
        self.progress.setRange(0, self.total)
        self.add(self.progress)

        self.status = QLabel()
        self.status.setProperty("ui_role", "subtitle")
        self.add(self.status)

        self.topic_lbl = QLabel()
        self.topic_lbl.setProperty("ui_role", "heading")
        self.add(self.topic_lbl)

        self.question = QLabel()
        self.question.setWordWrap(True)
        self.question.setStyleSheet("font-size: 16pt; font-weight: 700;")
        self.add(self.question)

        self.diagram_label = QLabel()
        self.diagram_label.setAlignment(Qt.AlignCenter)
        self.diagram_label.setVisible(False)
        self.add(self.diagram_label)

        self.answer = QLineEdit()
        self.answer.setPlaceholderText("Type your answer")
        self.answer.returnPressed.connect(self.check)
        self.add(self.answer)

        row = QHBoxLayout()
        check_btn = QPushButton("CHECK ANSWER")
        check_btn.clicked.connect(self.check)
        row.addWidget(check_btn)
        self.next_btn = QPushButton("NEXT →")
        self.next_btn.setProperty("ui_role", "secondary")
        self.next_btn.clicked.connect(self.next_question)
        self.next_btn.setEnabled(False)
        row.addWidget(self.next_btn)
        self.add_layout(row)

        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.add(self.hint)

        self.result = QLabel()
        self.result.setWordWrap(True)
        self.add(self.result)

        self.timer_label = QLabel()
        self.timer_label.setProperty("ui_role", "muted")
        self.add(self.timer_label)

        self.timer = CountdownTimer(self)
        self.timer.tick.connect(self.on_tick)
        self.timer.finished.connect(self.on_time_up)

        self.finish()
        self.next_question()

    def _pick_topic(self):
        if self.mode == "choose" and self.topics:
            return random.choice(self.topics)
        if self.mode == "speed":
            return self.ad.choose_topic("mixed")
        return self.ad.choose_topic(self.mode)

    def next_question(self):
        if self.answered >= self.total:
            self.finish_session()
            return

        topic = self._pick_topic()
        difficulty = self.ad.recommend_difficulty(topic) if self.mode == "recommended" else self.base_difficulty
        self.q = self.qe.generate(topic, difficulty)

        self.topic_lbl.setText(f"{self.q['topic_name']}  •  Difficulty {self.q['difficulty']}/4")
        self.question.setText(self.q["question"])

        if self.q.get("diagram"):
            pm = diagram_to_pixmap(self.q["diagram"], 300, 220)
            self.diagram_label.setPixmap(pm)
            self.diagram_label.setVisible(True)
        else:
            self.diagram_label.setVisible(False)

        self.hint.setText(("💡 " + self.q["hint"]) if self.show_hints else "")
        self.result.clear()
        self.answer.clear()
        self.answer.setEnabled(True)
        self.next_btn.setEnabled(False)
        self.status.setText(f"Question {self.answered+1} of {self.total}")
        self.progress.setValue(self.answered)

        if self.timed:
            self.timer.start(60)
        else:
            self.timer_label.clear()

    def on_tick(self, seconds):
        self.timer_label.setText(f"⏱ {seconds}s remaining")

    def on_time_up(self):
        if self.answer.isEnabled():
            self.check(timeout=True)

    def check(self, timeout=False):
        if not self.q or not self.answer.isEnabled():
            return
        self.timer.stop()
        user_text = self.answer.text().strip()
        correct = (not timeout) and answers_match(user_text, self.q["answer"])

        mastery = self.me.score(self.q["topic"], correct, self.q["difficulty"])
        self.answered += 1
        if correct:
            self.correct_count += 1

        s = self.app.student
        s.setdefault("history", []).append({
            "question_id": self.q["id"], "topic": self.q["topic"],
            "correct": correct, "difficulty": self.q["difficulty"]
        })
        s["today_done"] = s.get("today_done", 0) + 1
        if correct:
            s["xp"] = s.get("xp", 0) + (10 + self.q["difficulty"] * 2)

        if self.show_solution:
            if correct:
                self.result.setText(f"✓ CORRECT!  +XP\n\n{self.q['explanation']}\n\nMastery: {int(mastery*100)}%")
            else:
                note = " (time's up)" if timeout else ""
                self.result.setText(
                    f"✗ Not quite{note}\nCorrect answer: {self.q['answer']}\n\n{self.q['explanation']}\n\nMastery: {int(mastery*100)}%"
                )
        else:
            self.result.setText("✓ Recorded." if correct else "✗ Recorded.")

        self.answer.setEnabled(False)
        self.next_btn.setEnabled(True)
        self.app.save_student()

    def finish_session(self):
        s = self.app.student
        s["streak"] = s.get("streak", 0) + (1 if self.correct_count >= self.total * 0.6 else 0)
        self.app.save_student()
        accuracy = self.correct_count / self.total if self.total else 0
        rec = self.ad.next_action(self.q["topic"] if self.q else "", accuracy, None)
        self.question.setText("🏁 Session complete!")
        self.topic_lbl.setText(f"Score: {self.correct_count}/{self.total} ({int(accuracy*100)}%)")
        self.diagram_label.setVisible(False)
        self.answer.setVisible(False)
        self.hint.setText(rec)
        self.result.clear()
        self.next_btn.setEnabled(False)
        self.status.setText("Well done — return to Home or start another session.")
        home_btn = QPushButton("🏠 BACK TO HOME")
        home_btn.clicked.connect(self.app.show_home)
        self.add(home_btn)
        again_btn = QPushButton("🔁 PRACTICE AGAIN")
        again_btn.setProperty("ui_role", "secondary")
        again_btn.clicked.connect(lambda: self.app.show_practice())
        self.add(again_btn)
