import random
from engine.question_engine import QuestionEngine

TOPICS = QuestionEngine.TOPICS

class AdaptiveEngine:
    """Deterministic local 'AI-like' recommendation logic (no online API needed)."""
    def __init__(self, student):
        self.student = student
        self.mastery = student.setdefault("mastery", {t: 0.5 for t in TOPICS})
        for t in TOPICS:
            self.mastery.setdefault(t, 0.5)

    def choose_topic(self, mode="recommended"):
        items = list(self.mastery.items())
        if mode == "weakness":
            return min(items, key=lambda x: x[1])[0]
        if mode == "strength":
            return max(items, key=lambda x: x[1])[0]
        if mode == "mixed":
            return random.choice(TOPICS)
        if mode == "daily":
            return random.choice(TOPICS)
        # recommended: weighted toward weaker topics
        items.sort(key=lambda x: x[1])
        pool = items[:max(3, len(items)//2)]
        return random.choice(pool)[0]

    def choose_topics(self, mode, n=1):
        return [self.choose_topic(mode) for _ in range(n)]

    def recommend_difficulty(self, topic):
        m = self.mastery.get(topic, 0.5)
        if m < 0.40: return 1
        if m < 0.60: return 2
        if m < 0.80: return 3
        return 4

    def recommendation_text(self):
        items = sorted(self.mastery.items(), key=lambda x: x[1])
        weakest = items[0][0] if items else None
        if not weakest:
            return "Start with a mixed practice session to build your profile."
        m = self.mastery[weakest]
        name = weakest.replace("_", " ").title()
        if m < 0.40:
            return f"Your {name} mastery is low. Start with the topic Guide before practising."
        if m < 0.65:
            return f"Focus on {name} — a short weakness-recovery session will help."
        return "You're doing well across topics. Try a Mixed or Speed challenge."

    def next_action(self, topic, accuracy, avg_time_sec):
        """Rule-based recommendation after a practice session."""
        m = self.mastery.get(topic, 0.5)
        if m < 0.4:
            return "Recommend: revisit the Guide and worked examples before more questions."
        if accuracy >= 0.8 and avg_time_sec and avg_time_sec > 40:
            return "Recommend: Speed Practice — your accuracy is high but you can go faster."
        if accuracy < 0.5 and avg_time_sec and avg_time_sec < 15:
            return "Recommend: slow down — try Foundation difficulty and read each question carefully."
        if m > 0.85:
            return "Recommend: Strength Challenge at Elite difficulty."
        return "Recommend: continue with Standard practice on this topic."
