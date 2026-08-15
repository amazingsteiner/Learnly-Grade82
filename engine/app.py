import json
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QInputDialog

from ui.theme_manager import ThemeManager
from engine.question_engine import QuestionEngine

from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.learn import LearnScreen
from screens.topic_detail import TopicDetailScreen
from screens.practice import PracticeSetupScreen
from screens.practice_session import PracticeSessionScreen
from screens.papers import PapersScreen
from screens.paper_viewer import PaperViewerScreen
from screens.profile import ProfileScreen
from screens.settings import SettingsScreen
from screens.tutor import TutorScreen
from screens.labs import LabsScreen
from screens.geometry_lab import GeometryLabScreen
from screens.data_lab import DataLabScreen
from screens.probability_lab import ProbabilityLabScreen
from screens.mental_maths import MentalMathsScreen
from screens.science_learn import ScienceLearnScreen
from screens.science_topic_detail import ScienceTopicDetailScreen
from screens.quiz_mode import QuizModeScreen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STUDENTS = DATA / "students"
PAPERS = DATA / "papers"
EXPORTS = DATA / "exports"

for folder in (DATA, STUDENTS, PAPERS, EXPORTS):
    folder.mkdir(parents=True, exist_ok=True)

ACCESS_CODE = "children of the sun"


def create_default_student(code):
    now = datetime.now().isoformat()
    return {
        "code": code, "name": f"Student {code}",
        "grade": 8, "subject": "Mathematics", "term": 1,
        "daily_goal": 20, "today_done": 0,
        "daily_goal_date": datetime.now().strftime("%Y-%m-%d"),
        "streak": 0, "xp": 0, "level": 1,
        "created_at": now, "updated_at": now, "last_login": now,
        "mastery": {t: 0.5 for t in QuestionEngine.TOPICS},
        "topic_stats": {},
        "settings": {
            "theme": "Classic Elite", "font_scale": "Normal",
            "hints": True, "sound": True, "animations": True,
            "show_solutions": True, "confirm_reset": True,
            "difficulty_pref": "Standard"
        },
        "history": [], "papers": [], "mistakes": [],
        "strengths": [], "weaknesses": [], "mental_best_streak": 0,
        "schema_version": 2
    }


class LearnlyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learnly — Grade 8 Mathematics")
        self.resize(430, 780)
        self.root = ROOT

        self.theme = ThemeManager()
        self.student = None
        self.student_path = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.show_login()

    # ---------------- CORE ----------------

    def clear(self):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

    def save_student(self):
        if not self.student or not self.student_path:
            return False
        try:
            self.student["updated_at"] = datetime.now().isoformat()
            self.student_path.write_text(
                json.dumps(self.student, indent=2, ensure_ascii=False), encoding="utf-8")
            return True
        except Exception as e:
            print("Learnly save error:", e)
            return False

    def refresh_current_screen(self):
        w = self.stack.currentWidget()
        if w and hasattr(w, "refresh"):
            try:
                w.refresh()
            except Exception:
                pass

    # ---------------- LOGIN ----------------

    def show_login(self):
        self.clear()
        screen = LoginScreen(self.login)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def login(self, code):
        code = str(code).strip().upper()
        STUDENTS.mkdir(parents=True, exist_ok=True)
        path = STUDENTS / f"{code}.json"
        self.student_path = path

        if path.exists():
            try:
                self.student = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                QMessageBox.critical(self, "Student Data Error", str(e))
                return
            defaults = create_default_student(code)
            for k, v in defaults.items():
                self.student.setdefault(k, v)
            for topic, v in defaults["mastery"].items():
                self.student["mastery"].setdefault(topic, v)
            self.student["grade"] = 8  # force grade 8
        else:
            self.student = create_default_student(code)
            if not self.save_student():
                QMessageBox.critical(self, "Save Error", "Could not create the new student profile.")
                return

        today = datetime.now().strftime("%Y-%m-%d")
        if self.student.get("daily_goal_date") != today:
            self.student["daily_goal_date"] = today
            self.student["today_done"] = 0

        settings = self.student.get("settings", {})
        try:
            self.theme.set_theme(settings.get("theme", "Classic Elite"))
            self.theme.set_font_scale(settings.get("font_scale", "Normal"))
        except Exception:
            pass

        self.student["last_login"] = datetime.now().isoformat()
        self.save_student()
        self.show_home()

    # ---------------- NAVIGATION ----------------

    def _go(self, screen):
        self.save_student()
        self.clear()
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def show_home(self):
        self._go(HomeScreen(self))

    def show_learn(self):
        self._go(LearnScreen(self))

    def show_topic_detail(self, topic_id):
        self._go(TopicDetailScreen(self, topic_id))

    def show_practice(self, mode=None, topics=None):
        self._go(PracticeSetupScreen(self, mode=mode, topics=topics))

    def launch_practice_session(self, mode, topics, difficulty, count, timed, hints, show_solution):
        self._go(PracticeSessionScreen(
            self, mode=mode, topics=topics, difficulty=difficulty,
            count=count, timed=timed, hints=hints, show_solution=show_solution
        ))

    def show_papers(self):
        self._go(PapersScreen(self))

    def show_paper_viewer(self, paper_id):
        self._go(PaperViewerScreen(self, paper_id))

    def show_profile(self):
        self._go(ProfileScreen(self))

    def show_settings(self):
        self._go(SettingsScreen(self))

    def show_labs(self):
        self._go(LabsScreen(self))

    def show_geometry_lab(self):
        self._go(GeometryLabScreen(self))

    def show_data_lab(self):
        self._go(DataLabScreen(self))

    def show_probability_lab(self):
        self._go(ProbabilityLabScreen(self))

    def show_mental(self):
        self._go(MentalMathsScreen(self))

    def show_science(self):
        self._go(ScienceLearnScreen(self))

    def show_science_topic(self, topic_id):
        self._go(ScienceTopicDetailScreen(self, topic_id))

    def show_quiz(self, subject="math", topic_id=None):
        self._go(QuizModeScreen(self, subject=subject, topic_id=topic_id))

    def show_tutor_gate(self):
        code, ok = QInputDialog.getText(self, "Tutor Access", "Access code:")
        if ok and code.strip().lower() == ACCESS_CODE:
            self.show_tutor()
        elif ok:
            QMessageBox.warning(self, "Access denied", "Incorrect access code.")

    def show_tutor(self):
        self._go(TutorScreen(self))

    # ---------------- LIFECYCLE ----------------

    def closeEvent(self, event):
        self.save_student()
        event.accept()
