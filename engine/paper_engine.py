import json, random
from datetime import datetime
from pathlib import Path
from engine.question_engine import QuestionEngine
from engine.adaptive import AdaptiveEngine

TOPIC_TERM = {
    "whole_numbers": 1, "integers": 1, "exponents": 1, "patterns": 1,
    "algebraic_expressions": 2, "algebraic_equations": 2, "geometry_lines": 2,
    "pythagoras": 3, "area_perimeter": 3, "financial_maths": 3, "transformations": 3,
    "data_handling": 4, "probability": 4
}

PAPER_TYPES = [
    "Term / ATP Aligned", "Weakness Recovery", "Strength Challenge",
    "Diagnostic", "Mock Exam", "Custom Topic Paper"
]

DIFFICULTY_MAP = {"Foundation": 1, "Standard": 2, "Advanced": 3, "Elite": 4}


class PaperEngine:
    def __init__(self, root):
        self.root = Path(root)
        self.q = QuestionEngine()

    def generate(self, student, paper_type="Term / ATP Aligned", term=None,
                 topics=None, difficulty="Standard", count=15, time_minutes=45):
        ad = AdaptiveEngine(student)
        term = term or student.get("term", 1)
        diff = DIFFICULTY_MAP.get(difficulty, 2)

        if not topics:
            if paper_type == "Weakness Recovery":
                topics = student.get("weaknesses") or [ad.choose_topic("weakness")]
            elif paper_type == "Strength Challenge":
                topics = student.get("strengths") or [ad.choose_topic("strength")]
            elif paper_type == "Term / ATP Aligned":
                topics = [t for t, tm in TOPIC_TERM.items() if tm == int(term)]
            else:
                topics = QuestionEngine.TOPICS

        if not topics:
            topics = QuestionEngine.TOPICS

        questions = []
        section_map = {}
        for i in range(count):
            topic = topics[i % len(topics)]
            qdiff = diff if paper_type != "Diagnostic" else random.randint(1, 4)
            q = self.q.generate(topic, qdiff)
            q["number"] = i + 1
            questions.append(q)
            section_map.setdefault(topic, []).append(q["number"])

        total_marks = sum(q["marks"] for q in questions)
        paper_id = "P" + datetime.now().strftime("%Y%m%d%H%M%S")

        paper = {
            "paper_id": paper_id,
            "grade": 8,
            "subject": "Mathematics",
            "term": term,
            "type": paper_type,
            "difficulty": difficulty,
            "topics": topics,
            "marks": total_marks,
            "time_minutes": time_minutes,
            "created_at": datetime.now().isoformat(),
            "student_code": student.get("code", ""),
            "questions": questions,
            "sections": section_map
        }

        path = self.root / "data" / "papers" / f"{paper_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(paper, indent=2, ensure_ascii=False), encoding="utf-8")

        student.setdefault("papers", []).append({
            "id": paper_id, "type": paper_type, "term": term,
            "marks": total_marks, "created_at": paper["created_at"]
        })

        return paper, path

    def load(self, paper_id):
        path = self.root / "data" / "papers" / f"{paper_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")), path
        return None, path

    def list_papers(self, student_code=None):
        folder = self.root / "data" / "papers"
        folder.mkdir(parents=True, exist_ok=True)
        out = []
        for f in sorted(folder.glob("*.json"), reverse=True):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                if student_code is None or d.get("student_code") == student_code:
                    out.append(d)
            except Exception:
                continue
        return out
