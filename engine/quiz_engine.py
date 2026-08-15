"""Definitions Quiz mode: multiple-choice on key_vocabulary, pulled from Math or Science content."""
import random
from engine.content_loader import all_topics, load_topic_notes
from engine.science_engine import all_science_topics, load_science_topic


def _parse_vocab_entry(entry):
    """key_vocabulary entries look like 'Term — definition text'."""
    if "—" in entry:
        term, definition = entry.split("—", 1)
    elif "-" in entry:
        term, definition = entry.split("-", 1)
    else:
        return None
    return term.strip(), definition.strip()


class DefinitionsQuizEngine:
    def _collect_terms(self, subject):
        terms = []
        if subject == "math":
            for t in all_topics():
                data = load_topic_notes(t["id"])
                if not data:
                    continue
                for entry in data.get("key_vocabulary", []):
                    parsed = _parse_vocab_entry(entry)
                    if parsed:
                        terms.append({"term": parsed[0], "definition": parsed[1], "topic": data["name"]})
        else:  # science
            for t in all_science_topics():
                data = load_science_topic(t["id"])
                if not data:
                    continue
                for entry in data.get("key_vocabulary", []):
                    parsed = _parse_vocab_entry(entry)
                    if parsed:
                        terms.append({"term": parsed[0], "definition": parsed[1], "topic": data["name"]})
        return terms

    def generate(self, subject="math"):
        terms = self._collect_terms(subject)
        if len(terms) < 4:
            return None
        correct = random.choice(terms)
        distractors = random.sample(
            [t["term"] for t in terms if t["term"] != correct["term"]],
            k=min(3, len(terms) - 1)
        )
        options = distractors + [correct["term"]]
        random.shuffle(options)
        return {
            "question": f"Which term matches this definition?\n\n\"{correct['definition']}\"",
            "options": options,
            "answer": correct["term"],
            "topic": correct["topic"]
        }
