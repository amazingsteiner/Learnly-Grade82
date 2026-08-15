from PySide6.QtWidgets import QLabel, QPushButton, QComboBox, QVBoxLayout
from .base import Screen
from engine.quiz_engine import DefinitionsQuizEngine


class QuizModeScreen(Screen):
    def __init__(self, app, subject="math", topic_id=None):
        super().__init__(app, "🧠 Definitions Quiz")
        self.engine = DefinitionsQuizEngine()
        self.subject = subject
        self.score = 0
        self.asked = 0
        self.current = None
        self.option_buttons = []

        self.add(QLabel("SUBJECT"))
        self.subject_box = QComboBox()
        self.subject_box.addItems(["Mathematics", "Natural Sciences"])
        self.subject_box.setCurrentText("Natural Sciences" if subject == "science" else "Mathematics")
        self.subject_box.currentTextChanged.connect(self.change_subject)
        self.add(self.subject_box)

        self.score_label = QLabel()
        self.add(self.score_label)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 15pt; font-weight: 700;")
        self.add(self.question_label)

        self.options_container = QVBoxLayout()
        self.add_layout(self.options_container)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.add(self.feedback)

        next_btn = QPushButton("NEXT QUESTION →")
        next_btn.setProperty("ui_role", "secondary")
        next_btn.clicked.connect(self.next_question)
        self.add(next_btn)

        self.finish()
        self.next_question()

    def change_subject(self, text):
        self.subject = "science" if text == "Natural Sciences" else "math"
        self.score, self.asked = 0, 0
        self.next_question()

    def update_score(self):
        self.score_label.setText(f"Score: {self.score}/{self.asked}")

    def next_question(self):
        self._clear_options()
        self.feedback.clear()
        q = self.engine.generate(self.subject)
        if not q:
            self.question_label.setText("Not enough vocabulary loaded for a quiz yet.")
            return
        self.current = q
        self.question_label.setText(f"[{q['topic']}]\n\n{q['question']}")
        for opt in q["options"]:
            b = QPushButton(opt)
            b.clicked.connect(lambda checked=False, o=opt: self.answer(o))
            self.options_container.addWidget(b)
            self.option_buttons.append(b)
        self.update_score()

    def _clear_options(self):
        while self.options_container.count():
            item = self.options_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.option_buttons = []

    def answer(self, selected):
        if not self.current:
            return
        self.asked += 1
        correct = selected == self.current["answer"]
        if correct:
            self.score += 1
            self.feedback.setText(f"✓ Correct! {selected}")
            self.app.student["xp"] = self.app.student.get("xp", 0) + 5
        else:
            self.feedback.setText(f"✗ Not quite. Correct answer: {self.current['answer']}")
        self.app.save_student()
        for b in self.option_buttons:
            b.setEnabled(False)
        self.update_score()
