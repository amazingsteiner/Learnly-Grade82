"""Grade 8 Natural Sciences: definition/fact quiz generator (multiple choice + short answer)."""
import json
import random
from pathlib import Path
from functools import lru_cache

SCIENCE_DIR = Path(__file__).resolve().parents[1] / "content" / "grade8" / "science"


@lru_cache(maxsize=1)
def load_science_curriculum():
    path = SCIENCE_DIR / "curriculum.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"topics": []}


@lru_cache(maxsize=16)
def load_science_topic(topic_id):
    path = SCIENCE_DIR / f"{topic_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def all_science_topics():
    return load_science_curriculum().get("topics", [])


class ScienceQuizEngine:
    """Builds multiple-choice questions from a topic's quiz_facts + key_vocabulary."""

    def _all_facts(self):
        facts = []
        for t in all_science_topics():
            data = load_science_topic(t["id"])
            if not data:
                continue
            for qf in data.get("quiz_facts", []):
                facts.append({"topic": data["name"], "q": qf["q"], "a": qf["a"]})
        return facts

    def generate_mc(self, topic_id=None):
        facts = self._all_facts()
        pool = [f for f in facts if topic_id is None or
                load_science_topic(topic_id) and f["topic"] == load_science_topic(topic_id)["name"]]
        if not pool:
            pool = facts
        if not pool:
            return None

        correct = random.choice(pool)
        distractors = random.sample(
            [f["a"] for f in pool if f["a"] != correct["a"]],
            k=min(3, max(0, len(pool) - 1))
        )
        options = distractors + [correct["a"]]
        random.shuffle(options)
        return {
            "question": correct["q"],
            "options": options,
            "answer": correct["a"],
            "topic": correct["topic"]
        }
