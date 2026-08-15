from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QPushButton
from .base import Screen
from ui.widgets import Card
from ui.render import science_diagram_to_pixmap
from engine.science_engine import load_science_topic


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


class ScienceTopicDetailScreen(Screen):
    def __init__(self, app, topic_id):
        data = load_science_topic(topic_id)
        name = data["name"] if data else topic_id
        super().__init__(app, f"🔬 {name}")

        if not data:
            self.add(QLabel("Content not found for this topic."))
            self.finish()
            return

        self.add(Card(
            "Quiz yourself",
            "Test your recall of key terms and facts from this strand.",
            ("DEFINITIONS QUIZ", lambda: app.show_quiz(subject="science", topic_id=topic_id))
        ))

        if data.get("diagram"):
            img_frame = QFrame()
            img_frame.setObjectName("card")
            img_layout = QVBoxLayout(img_frame)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setPixmap(science_diagram_to_pixmap(data["diagram"], 320, 220))
            img_layout.addWidget(img_label)
            self.add(img_frame)

        self.add(section("1️⃣ What is it?", data.get("what_is_it", "")))
        self.add(section("2️⃣ Why it matters", data.get("why_it_matters", "")))
        self.add(section("3️⃣ Key vocabulary", data.get("key_vocabulary", [])))
        self.add(section("4️⃣ Core concept", data.get("core_concept", "")))
        self.add(section("5️⃣ Key facts", data.get("key_facts", [])))
        self.add(section("⚠️ Common misconceptions", data.get("common_misconceptions", [])))
        self.add(section("✅ Quick test", data.get("quick_test", [])))

        self.finish()
