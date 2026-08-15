from PySide6.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from .base import Screen
from ui.render import chart_to_pixmap
from engine.data_engine import DataEngine


class DataLabScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "📊 Data Handling Lab")
        self.de = DataEngine()

        sub = QLabel("Enter values, calculate real statistics (mean/median/mode/range/"
                      "quartiles/outliers), build a grouped frequency table, and generate graphs.")
        sub.setProperty("ui_role", "subtitle")
        sub.setWordWrap(True)
        self.add(sub)

        row = QHBoxLayout()
        self.rows_box = QSpinBox()
        self.rows_box.setRange(3, 30)
        self.rows_box.setValue(10)
        self.rows_box.valueChanged.connect(self.resize_table)
        row.addWidget(QLabel("Rows:"))
        row.addWidget(self.rows_box)
        random_btn = QPushButton("🎲 RANDOM DATA")
        random_btn.setProperty("ui_role", "secondary")
        random_btn.clicked.connect(self.random_fill)
        row.addWidget(random_btn)
        self.add_layout(row)

        self.table = QTableWidget(10, 1)
        self.table.setHorizontalHeaderLabels(["Value"])
        self.table.setMinimumHeight(280)
        self.add(self.table)

        calc = QPushButton("🧮 CALCULATE STATISTICS")
        calc.clicked.connect(self.calculate)
        self.add(calc)

        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        self.add(self.stats_label)

        self.outlier_label = QLabel("")
        self.outlier_label.setWordWrap(True)
        self.add(self.outlier_label)

        self.add(QLabel("GROUPED FREQUENCY TABLE (class intervals)"))
        self.freq_table = QTableWidget(0, 3)
        self.freq_table.setHorizontalHeaderLabels(["Class Interval", "Frequency", "Cumulative Freq."])
        self.freq_table.setMinimumHeight(160)
        self.add(self.freq_table)

        self.add(QLabel("GRAPH TYPE"))
        self.chart_type = QComboBox()
        self.chart_type.addItems(["bar", "pie", "line", "box", "histogram"])
        self.chart_type.currentTextChanged.connect(self.calculate)
        self.add(self.chart_type)

        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.add(self.chart_label)

        self.finish()

    def resize_table(self, n):
        self.table.setRowCount(n)

    def random_fill(self):
        vals = self.de.random_dataset(self.rows_box.value(), 1, 60)
        for i, v in enumerate(vals):
            self.table.setItem(i, 0, QTableWidgetItem(str(v)))
        self.calculate()

    def get_values(self):
        values = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item and item.text().strip():
                try:
                    values.append(float(item.text()))
                except ValueError:
                    pass
        return values

    def calculate(self):
        values = self.get_values()
        if not values:
            self.stats_label.setText("Enter numbers in the table (or tap RANDOM DATA).")
            self.outlier_label.clear()
            self.freq_table.setRowCount(0)
            self.chart_label.clear()
            return

        s = self.de.summary(values)
        self.stats_label.setText(
            f"Count: {s['count']}   Sum: {s['sum']:g}\n"
            f"Mean: {s['mean']:g}   Median: {s['median']:g}\n"
            f"Mode: {', '.join(f'{m:g}' for m in s['mode'])}\n"
            f"Range: {s['range']:g}   Min: {s['minimum']:g}   Max: {s['maximum']:g}\n"
            f"Q1: {s['q1']:g}   Q3: {s['q3']:g}   IQR: {s['iqr']:g}\n"
            f"Five-number summary: {tuple(round(x,2) for x in s['five_number_summary'])}"
        )
        if s["outliers"]:
            self.outlier_label.setText(f"⚠️ Possible outliers (beyond 1.5×IQR): {s['outliers']}")
        else:
            self.outlier_label.setText("No outliers detected (within 1.5×IQR of the quartiles).")

        grouped = self.de.grouped_frequency(values, n_classes=5)
        self.freq_table.setRowCount(len(grouped))
        for i, row in enumerate(grouped):
            self.freq_table.setItem(i, 0, QTableWidgetItem(row["class"]))
            self.freq_table.setItem(i, 1, QTableWidgetItem(str(row["frequency"])))
            self.freq_table.setItem(i, 2, QTableWidgetItem(str(row["cumulative_frequency"])))

        labels = [str(int(v)) if v == int(v) else str(v) for v in values]
        pm = chart_to_pixmap(values, labels, self.chart_type.currentText(), 320, 260)
        self.chart_label.setPixmap(pm)
