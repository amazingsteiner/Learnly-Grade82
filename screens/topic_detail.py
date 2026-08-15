from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QPushButton
from .base import Screen
from ui.widgets import Card
from engine.content_loader import load_topic_notes, topic_name, topic_icon, content_status


def section(title, body):
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 10, 14, 10)
    layout.setSpacing(4)
    h = QLabel(title)
    h.setProperty("ui_role", "heading")
    layout.addWidget(h)
    if isinstance(body, list):
        for item in body:
            lbl = QLabel(f"•  {item}")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)
    else:
        lbl = QLabel(str(body))
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
    return frame


class TopicDetailScreen(Screen):
    def __init__(self, app, topic_id):
        name = topic_name(topic_id)
        icon = topic_icon(topic_id)
        super().__init__(app, f"{icon} {name}")
        notes = load_topic_notes(topic_id)

        if not notes:
            status = content_status()
            self.add(QLabel(
                "Content not found for this topic.\n\n"
                f"Looked in: {status['content_dir']}\n"
                f"Folder exists: {status['exists']}  •  "
                f"curriculum.json found: {status['curriculum_found']}\n\n"
                "This usually means the content/ folder wasn't copied alongside "
                "the app. Re-check the project structure."
            ))
            self.finish()
            return

        mastery = app.student.get("mastery", {}).get(topic_id, 0.5)
        self.add(Card(
            "Your Mastery",
            f"{int(mastery*100)}% on {name}",
            ("PRACTICE THIS TOPIC", lambda: app.show_practice(mode="choose", topics=[topic_id])),
            ("QUIZ DEFINITIONS", lambda: app.show_quiz(subject="math", topic_id=topic_id))
        ))

        self.add(section("1️⃣ What is it?", notes.get("what_is_it", "")))
        self.add(section("2️⃣ Why it matters", notes.get("why_it_matters", "")))
        self.add(section("3️⃣ Key vocabulary", notes.get("key_vocabulary", [])))
        self.add(section("4️⃣ Core concept", notes.get("core_concept", "")))
        self.add(section("5️⃣ Rules", notes.get("rules", [])))
        self.add(section("6️⃣ Formulae", notes.get("formulae", [])))
        self.add(section("7️⃣ Step-by-step method", notes.get("step_by_step_method", [])))

        ex1 = notes.get("worked_example_1", {})
        if ex1:
            self.add(section("8️⃣ Worked example 1", f"Q: {ex1.get('question','')}\n\n{ex1.get('solution','')}"))

        ex2 = notes.get("worked_example_2", {})
        if ex2:
            self.add(section("9️⃣ Worked example 2", f"Q: {ex2.get('question','')}\n\n{ex2.get('solution','')}"))

        self.add(section("⚡ Fast method", notes.get("fast_method", "")))
        self.add(section("🧠 Why the fast method works", notes.get("why_fast_method_works", "")))
        self.add(section("⚠️ Common mistakes", notes.get("common_mistakes", [])))
        self.add(section("💡 Memory trick", notes.get("memory_trick", "")))
        self.add(section("👁 Visual explanation", notes.get("visual_explanation", "")))
        self.add(section("🧭 Guided example", notes.get("guided_example", "")))
        self.add(section("✏️ Practice questions", notes.get("practice_questions", [])))
        self.add(section("🏆 Challenge question", notes.get("challenge_question", "")))
        self.add(section("✅ Quick test", notes.get("quick_test", [])))
        self.add(section("🎓 Mastery check", notes.get("mastery_check", "")))

        practice_btn = QPushButton("✏️ PRACTICE THIS TOPIC NOW")
        practice_btn.clicked.connect(lambda: app.show_practice(mode="choose", topics=[topic_id]))
        self.add(practice_btn)

        self.finish()
