from PySide6.QtWidgets import QApplication

THEMES = {
    "Classic Elite": {
        "bg": "#F5F7FA", "surface": "#FFFFFF", "text": "#172033",
        "muted": "#667085", "accent": "#3157D5", "good": "#159A68", "bad": "#D64545"
    },
    "Midnight": {
        "bg": "#0E1422", "surface": "#182033", "text": "#F4F7FF",
        "muted": "#AAB4CA", "accent": "#6D8CFF", "good": "#34D399", "bad": "#F87171"
    },
    "Academic": {
        "bg": "#F4F0E7", "surface": "#FFFDF7", "text": "#302B23",
        "muted": "#746C60", "accent": "#7A4E2D", "good": "#397A5A", "bad": "#B23A3A"
    },
    "Neon": {
        "bg": "#101015", "surface": "#191922", "text": "#F8F8FF",
        "muted": "#A9A9B8", "accent": "#C45CFF", "good": "#33E6A0", "bad": "#FF5C8A"
    },
    "Glass": {
        "bg": "#EAF4F6", "surface": "#F9FEFF", "text": "#15323A",
        "muted": "#637E86", "accent": "#168AA3", "good": "#198754", "bad": "#C0392B"
    }
}

FONT_SCALES = {"Small": 0.85, "Normal": 1.0, "Large": 1.15, "Extra Large": 1.3}


class ThemeManager:
    def __init__(self):
        self.current = "Classic Elite"
        self.font_scale_name = "Normal"
        self.apply()

    def set_theme(self, name):
        if name not in THEMES:
            name = "Classic Elite"
        self.current = name
        self.apply()

    def set_font_scale(self, name):
        if name not in FONT_SCALES:
            name = "Normal"
        self.font_scale_name = name
        self.apply()

    def apply(self):
        c = THEMES[self.current]
        s = FONT_SCALES.get(self.font_scale_name, 1.0)

        def px(base):
            return max(10, round(base * s))

        QApplication.instance().setStyleSheet(f"""
            QWidget {{
                background: {c['bg']};
                color: {c['text']};
                font-family: "Sans Serif";
                font-size: {px(15)}px;
            }}
            QFrame#card {{
                background: {c['surface']};
                border-radius: 16px;
                border: 1px solid {c['muted']}33;
            }}
            QLabel[ui_role="title"] {{
                font-size: {px(26)}px; font-weight: 800;
            }}
            QLabel[ui_role="heading"] {{
                font-size: {px(19)}px; font-weight: 700;
            }}
            QLabel[ui_role="subtitle"] {{
                font-size: {px(14)}px; color: {c['muted']};
            }}
            QLabel[ui_role="muted"] {{
                font-size: {px(12)}px; color: {c['muted']};
            }}
            QPushButton {{
                background: {c['accent']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 8px 14px;
                min-height: {px(46)}px;
                font-size: {px(14)}px;
                font-weight: 600;
            }}
            QPushButton[ui_role="secondary"] {{
                background: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['muted']}55;
                min-height: {px(38)}px;
                font-size: {px(13)}px;
            }}
            QPushButton:hover {{ opacity: 0.92; }}
            QPushButton:disabled {{ background: {c['muted']}55; color: {c['muted']}; }}
            QLineEdit, QComboBox, QSpinBox {{
                background: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['muted']}77;
                border-radius: 10px;
                padding: 8px;
                min-height: {px(40)}px;
                font-size: {px(14)}px;
            }}
            QCheckBox {{ font-size: {px(14)}px; padding: 4px; }}
            QProgressBar {{
                border: 1px solid {c['muted']}55;
                border-radius: 10px;
                background: {c['surface']};
                min-height: {px(24)}px;
                text-align: center;
                font-size: {px(12)}px;
            }}
            QProgressBar::chunk {{
                background: {c['accent']};
                border-radius: 8px;
            }}
            QScrollArea {{ border: none; background: transparent; }}
            QTableWidget {{
                background: {c['surface']};
                color: {c['text']};
                gridline-color: {c['muted']}55;
                font-size: {px(13)}px;
            }}
            QHeaderView::section {{
                background: {c['accent']};
                color: white;
                padding: 6px;
                font-weight: 700;
                border: none;
            }}
        """)

    def colors(self):
        return THEMES[self.current]
