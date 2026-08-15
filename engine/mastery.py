class MasteryEngine:
    def __init__(self, student):
        self.student = student
        self.mastery = student.setdefault("mastery", {})

    def score(self, topic, correct, difficulty=1):
        old = float(self.mastery.get(topic, 0.5))
        step = 0.04 + min(0.04, difficulty * 0.01)
        new = old + (step if correct else -step * 1.25)
        new = max(0.0, min(1.0, round(new, 4)))
        self.mastery[topic] = new
        self.refresh()
        return new

    def refresh(self):
        items = sorted(self.mastery.items(), key=lambda x: x[1])
        self.student["weaknesses"] = [k for k, v in items if v < 0.55][:5]
        self.student["strengths"] = [k for k, v in reversed(items) if v >= 0.75][:5]

    def overall(self):
        vals = list(self.mastery.values())
        return sum(vals) / len(vals) if vals else 0.5
