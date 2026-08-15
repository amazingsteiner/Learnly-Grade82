import random
from PySide6.QtWidgets import QLabel, QPushButton, QComboBox, QSpinBox, QHBoxLayout
from PySide6.QtCore import Qt
from .base import Screen
from ui.render import chart_to_pixmap
from engine.probability_engine import ProbabilityEngine


class ProbabilityLabScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "🎲 Probability Lab")
        self.pe = ProbabilityEngine()
        self.results = []

        sub = QLabel("Run simulations and watch experimental probability approach theoretical probability.")
        sub.setProperty("ui_role", "subtitle")
        sub.setWordWrap(True)
        self.add(sub)

        self.add(QLabel("SIMULATION"))
        self.sim_box = QComboBox()
        self.sim_box.addItems(["Dice (1 die)", "Coin toss", "Spinner (8 sectors)", "Cards"])
        self.add(self.sim_box)

        row = QHBoxLayout()
        row.addWidget(QLabel("Trials:"))
        self.trials_box = QSpinBox()
        self.trials_box.setRange(1, 500)
        self.trials_box.setValue(20)
        row.addWidget(self.trials_box)
        self.add_layout(row)

        run = QPushButton("▶ RUN SIMULATION")
        run.clicked.connect(self.run)
        self.add(run)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.add(self.result_label)

        self.compare_label = QLabel("")
        self.compare_label.setWordWrap(True)
        self.compare_label.setProperty("ui_role", "heading")
        self.add(self.compare_label)

        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.add(self.chart_label)

        self.finish()

    def run(self):
        n = self.trials_box.value()
        sim = self.sim_box.currentText()

        if sim.startswith("Dice"):
            outcomes = self.pe.roll_die(6, n)
            freq = {i: outcomes.count(i) for i in range(1, 7)}
            labels = [str(i) for i in range(1, 7)]
            values = [freq[i] for i in range(1, 7)]
            theoretical = 1 / 6
            fav_label = "rolling a 6"
            experimental = freq[6] / n

        elif sim.startswith("Coin"):
            outcomes = self.pe.flip_coin(n)
            freq = {"Heads": outcomes.count("Heads"), "Tails": outcomes.count("Tails")}
            labels = list(freq.keys())
            values = list(freq.values())
            theoretical = 0.5
            fav_label = "Heads"
            experimental = freq["Heads"] / n

        elif sim.startswith("Spinner"):
            outcomes = self.pe.spin_spinner(8, n)
            freq = {i: outcomes.count(i) for i in range(1, 9)}
            labels = [str(i) for i in range(1, 9)]
            values = [freq[i] for i in range(1, 9)]
            theoretical = 1 / 8
            fav_label = "landing on 8"
            experimental = freq[8] / n

        else:  # Cards
            reds = 0
            outcomes = []
            for _ in range(n):
                card = self.pe.draw_card(1)[0]
                outcomes.append(card)
                if "♥" in card or "♦" in card:
                    reds += 1
            freq = {"Red": reds, "Black": n - reds}
            labels = list(freq.keys())
            values = list(freq.values())
            theoretical = 0.5
            fav_label = "a red card"
            experimental = reds / n

        self.result_label.setText(f"Outcomes ({n} trials): {outcomes[:30]}{' ...' if n>30 else ''}")
        self.compare_label.setText(
            f"THEORETICAL P({fav_label}) = {theoretical:.3f}\n"
            f"EXPERIMENTAL P({fav_label}) = {experimental:.3f}  ({n} trials)\n"
            f"Difference: {abs(theoretical-experimental):.3f}"
        )
        self.chart_label.setPixmap(chart_to_pixmap(values, labels, "bar", 320, 260))
