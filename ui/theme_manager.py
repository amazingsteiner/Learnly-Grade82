from PySide6.QtWidgets import QApplication

THEMES = {
    "Classic Elite": {
        "bg": "#F5F7FA", "surface": "#FFFFFF", "text": "#172033",
        "muted": "#667085", "accent": "#3157D5", "good": "#159A68"
    },
    "Midnight": {
        "bg": "#0E1422", "surface": "#182033", "text": "#F4F7FF",
        "muted": "#AAB4CA", "accent": "#6D8CFF", "good": "#34D399"
    },
    "Academic": {
        "bg": "#F4F0E7", "surface": "#FFFDF7", "text": "#302B23",
        "muted": "#746C60", "accent": "#7A4E2D", "good": "#397A5A"
    },
    "Neon": {
        "bg": "#101015", "surface": "#191922", "text": "#F8F8FF",
        "muted": "#A9A9B8", "accent": "#C45CFF", "good": "#33E6A0"
    },
    "Glass": {
        "bg": "#EAF4F6", "surface": "#F9FEFF", "text": "#15323A",
        "muted": "#637E86", "accent": "#168AA3", "good": "#198754"
    }
}

class ThemeManager:
    def __init__(self):
        self.current = "Classic Elite"
        self.set_theme(self.current)

    def set_theme(self, name):
        if name not in THEMES:
            name = "Classic Elite"
        self.current = name
        c = THEMES[name]
        QApplication.instance().setStyleSheet(f"""
            QWidget {{
                background: {c['bg']};
                color: {c['text']};
                font-family: Arial;
                font-size: 10pt;
            }}
            QFrame#card {{
                background: {c['surface']};
                border-radius: 14px;
            }}
            QPushButton {{
                background: {c['accent']};
                color: white;
                border: none;
                border-radius: 9px;
                padding: 9px 12px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
            QLineEdit, QComboBox {{
                background: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['muted']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
