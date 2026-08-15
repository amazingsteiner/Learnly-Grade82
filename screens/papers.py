from PySide6.QtWidgets import QLabel, QComboBox, QPushButton, QHBoxLayout, QSpinBox, QMessageBox
from .base import Screen
from ui.widgets import Card, BottomNav
from engine.paper_engine import PaperEngine, PAPER_TYPES, DIFFICULTY_MAP


class PapersScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "📝 Question Papers")
        self.pe = PaperEngine(app.root)

        self.add(QLabel("PAPER TYPE"))
        self.type_box = QComboBox()
        self.type_box.addItems(PAPER_TYPES)
        self.add(self.type_box)

        self.add(QLabel("TERM"))
        self.term_box = QComboBox()
        for t in [1, 2, 3, 4]:
            self.term_box.addItem(f"Term {t}", t)  # store the real int as itemData
        current_term = int(app.student.get("term", 1))
        idx = self.term_box.findData(current_term)
        self.term_box.setCurrentIndex(idx if idx >= 0 else 0)
        self.add(self.term_box)

        self.add(QLabel("DIFFICULTY"))
        self.diff_box = QComboBox()
        self.diff_box.addItems(list(DIFFICULTY_MAP.keys()))
        self.diff_box.setCurrentText("Standard")
        self.add(self.diff_box)

        self.add(QLabel("QUESTIONS"))
        self.count_box = QSpinBox()
        self.count_box.setRange(5, 40)
        self.count_box.setValue(15)
        self.add(self.count_box)

        self.add(QLabel("TIME LIMIT (minutes)"))
        self.time_box = QSpinBox()
        self.time_box.setRange(10, 180)
        self.time_box.setValue(45)
        self.add(self.time_box)

        generate = QPushButton("📝 GENERATE PAPER")
        generate.clicked.connect(self.generate)
        self.add(generate)

        self.add(QLabel("📂 PAPER LIBRARY"))
        self.refresh_library()

        self.add(BottomNav(app))
        self.finish()

    def refresh_library(self):
        papers = self.pe.list_papers(self.app.student.get("code"))
        if not papers:
            self.add(Card("No papers yet", "Generate your first paper above."))
            return
        for p in papers[:10]:
            self.add(Card(
                f"{p['type']} — Term {p['term']}",
                f"{p['marks']} marks • {len(p['questions'])} questions • {p['created_at'][:16].replace('T',' ')}",
                ("VIEW PAPER", lambda pid=p['paper_id']: self.app.show_paper_viewer(pid))
            ))

    def generate(self):
        selected_term = self.term_box.currentData()  # guaranteed correct int, no string parsing
        try:
            paper, path = self.pe.generate(
                self.app.student,
                paper_type=self.type_box.currentText(),
                term=selected_term,
                difficulty=self.diff_box.currentText(),
                count=self.count_box.value(),
                time_minutes=self.time_box.value()
            )
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", str(e))
            return

        self.app.save_student()
        QMessageBox.information(
            self, "Paper Generated",
            f"✓ {paper['type']} — Term {paper['term']}\n\n"
            f"ID: {paper['paper_id']}\nMarks: {paper['marks']}\n"
            f"Questions: {len(paper['questions'])}\n\nSaved to:\n{path}"
        )
        self.app.show_paper_viewer(paper["paper_id"])
