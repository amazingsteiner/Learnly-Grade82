from .base import Screen
from ui.widgets import Card, BottomNav


class LabsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "📐 Maths Labs")
        self.add(Card("📐 Geometry Drawer",
                      "Draw triangles, rectangles, circles, angles and coordinate points — no images needed.",
                      ("OPEN", app.show_geometry_lab)))
        self.add(Card("📊 Data Handling Lab",
                      "Enter data, calculate mean/median/mode/range, and generate bar, pie, line and box charts.",
                      ("OPEN", app.show_data_lab)))
        self.add(Card("🎲 Probability Lab",
                      "Simulate dice, coins, spinners and cards — compare experimental vs theoretical probability.",
                      ("OPEN", app.show_probability_lab)))
        self.add(Card("🧮 Mental Maths",
                      "Fast calculation tricks with a timer, streaks and personal bests.",
                      ("OPEN", app.show_mental)))
        self.add(Card("🧠 Definitions Quiz",
                      "Multiple-choice quiz on key terms from Maths or Natural Sciences.",
                      ("OPEN", app.show_quiz)))
        self.add(BottomNav(app))
        self.finish()
