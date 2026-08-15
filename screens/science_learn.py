from PySide6.QtWidgets import QLabel
from .base import Screen
from ui.widgets import TopicTile, BottomNav
from engine.science_engine import all_science_topics


class ScienceLearnScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "🔬 Natural Sciences")

        sub = QLabel("Grade 8 CAPS Natural Sciences — the four core strands, with code-generated diagrams.")
        sub.setProperty("ui_role", "subtitle")
        sub.setWordWrap(True)
        self.add(sub)

        for t in all_science_topics():
            tile = TopicTile(
                t.get("icon", "🔬"), t["name"],
                "Tap to open notes, key facts and a diagram.",
                on_open=lambda tid=t["id"]: app.show_science_topic(tid),
                on_practice=lambda: app.show_quiz(subject="science")
            )
            self.add(tile)

        self.add(BottomNav(app))
        self.finish()
