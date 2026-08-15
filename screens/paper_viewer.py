from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor
from PySide6.QtWidgets import QLabel, QPushButton, QFrame, QVBoxLayout, QHBoxLayout, QMessageBox
from .base import Screen
from engine.paper_engine import PaperEngine
from ui.render import diagram_to_pixmap


class PaperViewerScreen(Screen):
    def __init__(self, app, paper_id):
        super().__init__(app, "📝 Paper Viewer")
        self.pe = PaperEngine(app.root)
        self.paper, self.path = self.pe.load(paper_id)
        self.showing_memo = False

        if not self.paper:
            self.add(QLabel("Paper not found."))
            self.finish()
            return

        p = self.paper
        header = QFrame()
        header.setObjectName("card")
        hl = QVBoxLayout(header)
        hl.addWidget(self._label(f"Grade 8 Mathematics — {p['type']}", "heading"))
        hl.addWidget(self._label(
            f"Term {p['term']} • {p['difficulty']} • {p['marks']} marks • {p.get('time_minutes',45)} min\n"
            f"Student: {p.get('student_code','')} • Created: {p['created_at'][:16].replace('T',' ')}"
        ))
        self.add(header)

        row = QHBoxLayout()
        self.memo_btn = QPushButton("VIEW MEMO")
        self.memo_btn.clicked.connect(self.toggle_memo)
        row.addWidget(self.memo_btn)
        export_img_btn = QPushButton("EXPORT AS IMAGE")
        export_img_btn.setProperty("ui_role", "secondary")
        export_img_btn.clicked.connect(self.export_image)
        row.addWidget(export_img_btn)
        self.add_layout(row)

        self.questions_container = QVBoxLayout()
        self.add_layout(self.questions_container)
        self.render_questions()

        self.finish()

    def _label(self, text, role=None):
        l = QLabel(text)
        l.setWordWrap(True)
        if role:
            l.setProperty("ui_role", role)
        return l

    def render_questions(self):
        while self.questions_container.count():
            item = self.questions_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for q in self.paper["questions"]:
            card = QFrame()
            card.setObjectName("card")
            layout = QVBoxLayout(card)
            layout.addWidget(self._label(
                f"Q{q['number']}. ({q['marks']} marks) — {q['topic_name']}", "heading"))
            layout.addWidget(self._label(q["question"]))

            if q.get("diagram"):
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setPixmap(diagram_to_pixmap(q["diagram"], 260, 180))
                layout.addWidget(img_label)

            if self.showing_memo:
                layout.addWidget(self._label(f"✅ Answer: {q['answer']}"))
                layout.addWidget(self._label(f"Working: {q['explanation']}"))
                layout.addWidget(self._label(f"Technique: {q['hint']}"))
            self.questions_container.addWidget(card)

    def toggle_memo(self):
        self.showing_memo = not self.showing_memo
        self.memo_btn.setText("HIDE MEMO" if self.showing_memo else "VIEW MEMO")
        self.render_questions()

    def export_image(self):
        """Composite the whole paper (questions + diagrams + memo) into one tall PNG."""
        export_dir = self.app.root / "data" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        p = self.paper
        page_w = 900
        row_h_est = 130
        diagram_h = 190
        total_h = 260 + sum(
            row_h_est + (diagram_h if q.get("diagram") else 0) + 90
            for q in p["questions"]
        )

        pixmap = QPixmap(page_w, total_h)
        pixmap.fill(QColor("#ffffff"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        y = 20
        painter.setFont(QFont("Sans", 18, QFont.Bold))
        painter.drawText(QRectF(30, y, page_w - 60, 40), f"Grade 8 Mathematics — {p['type']}")
        y += 44
        painter.setFont(QFont("Sans", 11))
        painter.drawText(QRectF(30, y, page_w - 60, 60),
            f"Term {p['term']} | {p['difficulty']} | {p['marks']} marks | {p.get('time_minutes',45)} min\n"
            f"Student: {p.get('student_code','')} | Created: {p['created_at'][:16].replace('T',' ')}")
        y += 70
        painter.drawLine(30, y, page_w - 30, y)
        y += 20

        for q in p["questions"]:
            painter.setFont(QFont("Sans", 13, QFont.Bold))
            painter.drawText(QRectF(30, y, page_w - 60, 24),
                              f"Q{q['number']} ({q['marks']} marks) — {q['topic_name']}")
            y += 28
            painter.setFont(QFont("Sans", 12))
            qrect = QRectF(30, y, page_w - 60, 60)
            painter.drawText(qrect, Qt.TextWordWrap, q["question"])
            y += 66

            if q.get("diagram"):
                dpix = diagram_to_pixmap(q["diagram"], 280, diagram_h - 20)
                painter.drawPixmap(50, y, dpix)
                y += diagram_h

            painter.setFont(QFont("Sans", 11))
            painter.setPen(QColor("#159A68"))
            painter.drawText(QRectF(30, y, page_w - 60, 20), f"Memo — Answer: {q['answer']}")
            y += 20
            painter.setPen(QColor("#555555"))
            painter.drawText(QRectF(30, y, page_w - 60, 40), Qt.TextWordWrap, f"Working: {q['explanation']}")
            y += 46
            painter.setPen(QColor("#000000"))
            painter.drawLine(30, y, page_w - 30, y)
            y += 16

        painter.end()

        out_path = export_dir / f"{p['paper_id']}.png"
        pixmap.save(str(out_path), "PNG")
        QMessageBox.information(self, "Exported as Image", f"Full paper (with memo) saved as an image:\n{out_path}")
