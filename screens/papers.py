from .base import Screen
from ui.widgets import Card, BottomNav
from PySide6.QtWidgets import QPushButton, QComboBox, QLabel

class PapersScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Question Papers")
        self.add(Card(
            "📝 Generate Question Paper",
            "Term-aware, personalised assessment generation.",
            ("GENERATE", self.generate)
        ))
        self.add(Card(
            "📂 Paper Library",
            "Generated papers will appear here and can be opened and reviewed."
        ))
        self.add(BottomNav(app))
        self.finish()

    def generate(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Paper Generator",
            "Next module: ATP term selection, weakness/strength weighting, "
            "marks, difficulty, questions and memorandum."
        )
