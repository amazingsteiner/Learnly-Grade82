from PySide6.QtWidgets import QLabel
from .base import Screen
from ui.widgets import TopicTile, BottomNav
from engine.content_loader import all_topics


class LearnScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "📚 Learn")

        sub = QLabel("Deep notes, guides and worked examples for every Grade 8 topic.")
        sub.setProperty("ui_role", "subtitle")
        sub.setWordWrap(True)
        self.add(sub)

        by_term = {1: [], 2: [], 3: [], 4: []}
        for t in all_topics():
            by_term.setdefault(t.get("term", 1), []).append(t)

        for term in [1, 2, 3, 4]:
            topics = by_term.get(term, [])
            if not topics:
                continue
            header = QLabel(f"TERM {term}")
            header.setProperty("ui_role", "muted")
            self.add(header)
            for t in topics:
                tile = TopicTile(
                    t.get("icon", "📘"), t["name"],
                    "Tap to open the full learning module.",
                    on_open=lambda tid=t["id"]: app.show_topic_detail(tid),
                    on_practice=lambda tid=t["id"]: app.show_practice(mode="choose", topics=[tid])
                )
                self.add(tile)

        self.add(BottomNav(app))
        self.finish()
