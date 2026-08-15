from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout, QFrame,
    QCheckBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .base import Screen
from ui.widgets import Card
from engine.content_loader import all_topics

MODES = [
    "Choose Topic", "Daily Practice", "Recommended Practice",
    "Weakness Practice", "Strength Challenge", "Mixed Practice",
    "Speed Practice", "Mental Maths"
]

DIFFICULTIES = ["Foundation", "Standard", "Advanced", "Elite"]
DIFF_MAP = {"Foundation": 1, "Standard": 2, "Advanced": 3, "Elite": 4}


class PracticeSetupScreen(Screen):
    def __init__(self, app, mode=None, topics=None):
        super().__init__(app, "✏️ Practice")

        sub = QLabel("Choose what you want to practise.")
        sub.setProperty("ui_role", "subtitle")
        self.add(sub)

        self.add(QLabel("MODE"))
        self.mode_box = QComboBox()
        self.mode_box.addItems(MODES)
        if mode:
            label_map = {"recommended": "Recommended Practice", "weakness": "Weakness Practice",
                         "strength": "Strength Challenge", "mixed": "Mixed Practice",
                         "choose": "Choose Topic", "daily": "Daily Practice"}
            self.mode_box.setCurrentText(label_map.get(mode, mode) if mode in label_map else mode)
        self.mode_box.currentTextChanged.connect(self.on_mode_change)
        self.add(self.mode_box)

        self.topic_label = QLabel("TOPICS (select one or more)")
        self.add(self.topic_label)

        self.topic_list = QListWidget()
        self.topic_list.setMinimumHeight(280)
        self.topic_list.setStyleSheet(
            "QListWidget::item { padding: 10px 4px; } "
            "QListWidget::indicator { width: 26px; height: 26px; }"
        )
        big_font = QFont("Sans", 14)
        for t in all_topics():
            item = QListWidgetItem(f"{t.get('icon','📘')} {t['name']}")
            item.setFont(big_font)
            item.setData(Qt.UserRole, t["id"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.topic_list.addItem(item)
        if topics:
            for i in range(self.topic_list.count()):
                item = self.topic_list.item(i)
                if item.data(Qt.UserRole) in topics:
                    item.setCheckState(Qt.Checked)
        self.add(self.topic_list)

        self.add(QLabel("DIFFICULTY"))
        diff_row = QHBoxLayout()
        self.diff_buttons = {}
        self.selected_diff = "Standard"
        for d in DIFFICULTIES:
            b = QPushButton(d)
            b.setProperty("ui_role", "secondary")
            b.clicked.connect(lambda checked=False, dd=d: self.select_diff(dd))
            diff_row.addWidget(b)
            self.diff_buttons[d] = b
        self.add_layout(diff_row)
        self.select_diff("Standard")

        self.add(QLabel("NUMBER OF QUESTIONS"))
        count_row = QHBoxLayout()
        self.count_buttons = {}
        self.selected_count = 10
        for c in [5, 10, 15, 20]:
            b = QPushButton(str(c))
            b.setProperty("ui_role", "secondary")
            b.clicked.connect(lambda checked=False, cc=c: self.select_count(cc))
            count_row.addWidget(b)
            self.count_buttons[c] = b
        self.add_layout(count_row)
        self.select_count(10)

        self.timed_box = QCheckBox("⏱ Timed")
        self.add(self.timed_box)
        self.hints_box = QCheckBox("💡 Hints")
        self.hints_box.setChecked(True)
        self.add(self.hints_box)
        self.solution_box = QCheckBox("✅ Show solution after each answer")
        self.solution_box.setChecked(True)
        self.add(self.solution_box)

        start = QPushButton("🚀 START PRACTICE")
        start.clicked.connect(self.start)
        self.add(start)

        self.on_mode_change(self.mode_box.currentText())
        self.finish()

    def select_diff(self, d):
        self.selected_diff = d
        for name, btn in self.diff_buttons.items():
            btn.setProperty("ui_role", "primary" if name == d else "secondary")
            btn.setStyle(btn.style())

    def select_count(self, c):
        self.selected_count = c
        for name, btn in self.count_buttons.items():
            btn.setProperty("ui_role", "primary" if name == c else "secondary")
            btn.setStyle(btn.style())

    def on_mode_change(self, mode_text):
        needs_topics = mode_text == "Choose Topic"
        self.topic_label.setVisible(needs_topics)
        self.topic_list.setVisible(needs_topics)

    def start(self):
        mode_text = self.mode_box.currentText()
        if mode_text == "Mental Maths":
            self.app.show_mental()
            return

        mode_map = {
            "Daily Practice": "daily", "Recommended Practice": "recommended",
            "Weakness Practice": "weakness", "Strength Challenge": "strength",
            "Mixed Practice": "mixed", "Speed Practice": "speed", "Choose Topic": "choose"
        }
        mode = mode_map.get(mode_text, "recommended")

        selected_topics = []
        if mode == "choose":
            for i in range(self.topic_list.count()):
                item = self.topic_list.item(i)
                if item.checkState() == Qt.Checked:
                    selected_topics.append(item.data(Qt.UserRole))
            if not selected_topics:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Choose a topic", "Please select at least one topic to practise.")
                return

        self.app.launch_practice_session(
            mode=mode,
            topics=selected_topics,
            difficulty=DIFF_MAP[self.selected_diff],
            count=self.selected_count,
            timed=self.timed_box.isChecked(),
            hints=self.hints_box.isChecked(),
            show_solution=self.solution_box.isChecked()
        )
