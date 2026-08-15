from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from engine.adaptive import AdaptiveEngine
from engine.answer_check import answers_match
from engine.content_loader import all_topics, load_topic_notes, topic_name
from engine.mastery import MasteryEngine
from engine.paper_engine import PaperEngine
from engine.question_engine import QuestionEngine


DEV_CODE = "DEV-2026"
PAPER_COST = 400


def default_student(code: str) -> dict:
    now = datetime.now().isoformat()
    return {
        "code": code,
        "name": f"Student {code}",
        "grade": 8,
        "subject": "Mathematics",
        "term": 1,
        "daily_goal": 20,
        "today_done": 0,
        "streak": 0,
        "xp": 0,
        "level": 1,
        "created_at": now,
        "updated_at": now,
        "last_login": now,
        "mastery": {topic: 0.5 for topic in QuestionEngine.TOPICS},
        "topic_stats": {},
        "history": [],
        "papers": [],
        "mistakes": [],
        "strengths": [],
        "weaknesses": [],
        "credits": 0,
        "credit_transactions": [],
        "dev_mode": False,
        "schema_version": 4,
    }


class Learnly(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.data_dir = Path(self.paths.data) / "learnly_data"
        self.students_dir = self.data_dir / "students"
        self.students_dir.mkdir(parents=True, exist_ok=True)
        self.papers_dir = self.data_dir / "papers"
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.student = None
        self.student_path = None
        self.practice_mode = "recommended"
        self.practice_count = 5
        self.practice_topics = []
        self.practice_questions = []
        self.practice_index = 0
        self.practice_correct = 0
        self.current_topic = None
        self.show_login()
        self.main_window.show()

    def save(self):
        if not self.student or not self.student_path:
            return
        self.student["updated_at"] = datetime.now().isoformat()
        self.student_path.write_text(
            json.dumps(self.student, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def credit_transaction(self, kind: str, amount: int, meta: dict | None = None):
        before = int(self.student.get("credits", 0))
        after = max(0, before + amount)
        self.student["credits"] = after
        self.student.setdefault("credit_transactions", []).append(
            {
                "id": "TX-" + datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "type": kind,
                "credits": amount,
                "balance_before": before,
                "balance_after": after,
                "timestamp": datetime.now().isoformat(),
                **(meta or {}),
            }
        )
        self.save()

    def set_content(self, title: str, children: list, back: bool = False):
        root = toga.Box(style=Pack(direction=COLUMN, padding=12))
        header = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
        if back:
            header.add(toga.Button("‹ Back", on_press=lambda *_: self.show_home(), style=Pack(padding_right=8)))
        header.add(toga.Label(title, style=Pack(font_size=20, font_weight="bold", flex=1)))
        root.add(header)

        body = toga.Box(style=Pack(direction=COLUMN, padding_bottom=8))
        for child in children:
            body.add(child)
        root.add(toga.ScrollContainer(content=body, style=Pack(flex=1), horizontal=False))
        self.main_window.content = root

    def label(self, text: str, size: int = 14, bold: bool = False):
        return toga.Label(text, style=Pack(font_size=size, font_weight="bold" if bold else "normal", padding_bottom=8))

    def button(self, text: str, callback):
        return toga.Button(text, on_press=callback, style=Pack(padding=8, padding_bottom=6))

    def show_login(self):
        code = toga.TextInput(placeholder="Student code", style=Pack(padding_bottom=10))
        status = toga.Label("", style=Pack(color="#B00020", padding_bottom=8))

        def login(_widget):
            value = code.value.strip().upper()
            if not value:
                status.text = "Enter a student code."
                return
            self.load_student(value)
            self.show_home()

        root = toga.Box(style=Pack(direction=COLUMN, padding=24))
        root.add(self.label("LEARNLY", 34, True))
        root.add(self.label("Grade 8 • Offline Mathematics", 18, True))
        root.add(self.label("Adaptive learning without internet access.", 14))
        root.add(code)
        root.add(status)
        root.add(self.button("ENTER LEARNLY", login))
        root.add(self.label("Progress is stored locally on the device.", 11))
        self.main_window.content = root

    def load_student(self, code: str):
        path = self.students_dir / f"{code}.json"
        if path.exists():
            try:
                student = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                student = default_student(code)
        else:
            student = default_student(code)
        defaults = default_student(code)
        for key, value in defaults.items():
            student.setdefault(key, value)
        for topic in QuestionEngine.TOPICS:
            student.setdefault("mastery", {}).setdefault(topic, 0.5)
        student["grade"] = 8
        student["last_login"] = datetime.now().isoformat()
        self.student = student
        self.student_path = path
        self.save()

    def show_home(self):
        s = self.student
        mastery = sum(s.get("mastery", {}).values()) / max(1, len(QuestionEngine.TOPICS))
        children = [
            self.label(f"🪙 {s.get('credits', 0):,} credits", 22, True),
            self.label(f"Level {s.get('level', 1)} • {s.get('xp', 0):,} XP • Mastery {mastery * 100:.0f}%"),
            self.button("📚 Learn", lambda *_: self.show_learn()),
            self.button("✍ Practice", lambda *_: self.show_practice()),
            self.button("📄 Paper Generator", lambda *_: self.show_papers()),
            self.button("🎯 Weakness Recovery", lambda *_: self.start_practice("weakness", 5)),
            self.button("👤 Profile", lambda *_: self.show_profile()),
            self.button("⚙ Settings", lambda *_: self.show_settings()),
        ]
        if s.get("dev_mode"):
            children.append(self.button("🔧 Developer Store", lambda *_: self.show_dev_store()))
        else:
            children.append(self.button("Developer Mode", lambda *_: self.show_dev_gate()))
        self.set_content("Learnly", children)

    def show_learn(self):
        children = []
        for topic in all_topics():
            tid = topic["id"]
            mastery = self.student.get("mastery", {}).get(tid, 0.5)
            children.append(
                self.button(
                    f"{topic.get('icon', '📘')} {topic['name']} • {mastery * 100:.0f}%",
                    lambda _w, t=tid: self.show_topic(t),
                )
            )
        self.set_content("Learn", children, back=True)

    def show_topic(self, topic_id: str):
        self.current_topic = topic_id
        notes = load_topic_notes(topic_id) or {}
        children = [self.label(topic_name(topic_id), 22, True)]
        for heading, key in [
            ("What is it?", "what_is_it"),
            ("Why it matters", "why_it_matters"),
            ("Core concept", "core_concept"),
            ("Rules", "rules"),
            ("Formulae", "formulae"),
            ("Step-by-step", "step_by_step_method"),
            ("Worked example", "worked_example_1"),
            ("Common mistakes", "common_mistakes"),
            ("Memory trick", "memory_trick"),
        ]:
            value = notes.get(key)
            if value:
                children.append(self.label(heading, 16, True))
                children.append(self.label(str(value), 13))
        children.append(self.button("Practice this topic", lambda *_: self.start_practice("topic", 5, [topic_id])))
        self.set_content("Topic", children, back=True)

    def show_practice(self):
        children = [
            self.label("Practice mode", 20, True),
            self.button("Recommended", lambda *_: self.start_practice("recommended", 5)),
            self.button("Mixed", lambda *_: self.start_practice("mixed", 5)),
            self.button("Strength Challenge", lambda *_: self.start_practice("strength", 5)),
            self.button("Weakness Recovery", lambda *_: self.start_practice("weakness", 5)),
            self.label("Question count", 16, True),
            self.button("5 questions", lambda *_: self.start_practice("recommended", 5)),
            self.button("10 questions", lambda *_: self.start_practice("recommended", 10)),
            self.button("20 questions", lambda *_: self.start_practice("recommended", 20)),
        ]
        self.set_content("Practice", children, back=True)

    def start_practice(self, mode: str, count: int, topics=None):
        self.practice_mode = mode
        self.practice_count = count
        self.practice_topics = topics or []
        self.practice_index = 0
        self.practice_correct = 0
        self.practice_questions = []
        qengine = QuestionEngine()
        adaptive = AdaptiveEngine(self.student)
        if self.practice_topics:
            topics_to_use = self.practice_topics
        else:
            if mode == "weakness":
                topics_to_use = adaptive.choose_topics("weakness", count)
            elif mode == "strength":
                topics_to_use = adaptive.choose_topics("strength", count)
            else:
                topics_to_use = list(QuestionEngine.TOPICS)
        if not topics_to_use:
            topics_to_use = list(QuestionEngine.TOPICS)
        for i in range(count):
            topic = topics_to_use[i % len(topics_to_use)]
            difficulty = adaptive.recommend_difficulty(topic) if mode == "recommended" else 2
            self.practice_questions.append(qengine.generate(topic, difficulty))
        self.show_question()

    def show_question(self):
        if self.practice_index >= len(self.practice_questions):
            self.finish_practice()
            return
        q = self.practice_questions[self.practice_index]
        answer = toga.TextInput(placeholder="Your answer", style=Pack(padding_bottom=8))
        feedback = toga.Label("", style=Pack(padding_bottom=8))

        def check(_widget):
            ok = answers_match(answer.value, q["answer"])
            self.practice_correct += int(ok)
            MasteryEngine(self.student).score(q["topic"], ok, q["difficulty"])
            self.student["today_done"] = self.student.get("today_done", 0) + 1
            self.student["xp"] = self.student.get("xp", 0) + (10 if ok else 3)
            self.student["level"] = 1 + self.student["xp"] // 500
            if ok:
                feedback.text = "✓ Correct\n" + q.get("explanation", "")
            else:
                feedback.text = "✗ Not quite. Answer: " + str(q["answer"]) + "\n" + q.get("explanation", "")
            self.save()
            self.practice_index += 1
            self.main_window.content = toga.Box(children=[
                self.label("Answer recorded", 18, True),
                feedback,
                self.button("NEXT", lambda *_: self.show_question()),
            ], style=Pack(direction=COLUMN, padding=20))

        children = [
            self.label(f"Question {self.practice_index + 1}/{len(self.practice_questions)}", 18, True),
            self.label(f"{q['topic_name']} • Difficulty {q['difficulty']} • {q['marks']} mark(s)", 12),
            self.label(q["question"], 17),
            answer,
            self.button("CHECK ANSWER", check),
        ]
        self.set_content("Practice Session", children, back=False)

    def finish_practice(self):
        total = len(self.practice_questions)
        self.student.setdefault("history", []).append({
            "type": "practice",
            "correct": self.practice_correct,
            "total": total,
            "date": datetime.now().isoformat(),
        })
        self.save()
        children = [
            self.label("Practice complete", 24, True),
            self.label(f"Score: {self.practice_correct}/{total}"),
            self.button("RETURN HOME", lambda *_: self.show_home()),
        ]
        self.set_content("Results", children)

    def show_papers(self):
        children = [
            self.label(f"Paper generation cost: {PAPER_COST} credits", 17, True),
            self.label(f"Current balance: {self.student.get('credits', 0)}"),
            self.button("Generate Term / ATP Paper", lambda *_: self.generate_paper("Term / ATP Aligned")),
            self.button("Generate Weakness Paper", lambda *_: self.generate_paper("Weakness Recovery")),
            self.button("Generate Strength Paper", lambda *_: self.generate_paper("Strength Challenge")),
            self.button("Generate Mock Exam", lambda *_: self.generate_paper("Mock Exam")),
        ]
        self.set_content("Paper Generator", children, back=True)

    def generate_paper(self, paper_type: str):
        if self.student.get("credits", 0) < PAPER_COST:
            children = [
                self.label("Not enough credits", 22, True),
                self.label(f"You need {PAPER_COST} credits."),
                self.button("Return", lambda *_: self.show_papers()),
            ]
            self.set_content("Paper Generator", children, back=True)
            return
        engine = PaperEngine(self.data_dir.parent)
        try:
            paper, path = engine.generate(self.student, paper_type=paper_type, term=self.student.get("term", 1), count=15)
            self.credit_transaction("paper_generation", -PAPER_COST, {"paper_id": paper["paper_id"]})
            self.save()
            preview = [
                self.label("Paper generated", 22, True),
                self.label(f"ID: {paper['paper_id']}"),
                self.label(f"Type: {paper_type}"),
                self.label(f"Marks: {paper['marks']} • Time: {paper['time_minutes']} minutes"),
            ]
            for q in paper["questions"][:5]:
                preview.append(self.label(f"{q['number']}. {q['question']}", 13))
            preview.append(self.label(f"Saved locally: {path.name}", 11))
            preview.append(self.button("Return Home", lambda *_: self.show_home()))
            self.set_content("Generated Paper", preview, back=True)
        except Exception as exc:
            self.set_content("Paper Error", [self.label(f"Could not generate paper: {exc}"), self.button("Back", lambda *_: self.show_home())], back=True)

    def show_dev_gate(self):
        code = toga.TextInput(placeholder="Developer code", style=Pack(padding_bottom=8))
        status = toga.Label("", style=Pack(color="#B00020", padding_bottom=8))

        def activate(_widget):
            if code.value.strip() == DEV_CODE:
                self.student["dev_mode"] = True
                self.save()
                self.show_dev_store()
            else:
                status.text = "Invalid developer code."

        self.set_content("Developer Mode", [self.label("Development tools", 22, True), code, status, self.button("ACTIVATE", activate)], back=True)

    def show_dev_store(self):
        packs = [("Starter", 2000), ("Exam Prep", 6000), ("Ultimate", 15000), ("Mega", 30000)]
        children = [self.label("Offline developer credit store", 20, True)]
        for name, credits in packs:
            children.append(self.button(f"Add {credits:,} credits • {name}", lambda _w, c=credits, n=name: self.add_dev_credits(n, c)))
        children.append(self.button("Clear credits", lambda *_: self.clear_credits()))
        self.set_content("Developer Store", children, back=True)

    def add_dev_credits(self, pack: str, credits: int):
        self.credit_transaction("dev_purchase", credits, {"pack": pack})
        self.show_dev_store()

    def clear_credits(self):
        self.credit_transaction("dev_reset", -int(self.student.get("credits", 0)))
        self.show_dev_store()

    def show_profile(self):
        s = self.student
        children = [
            self.label(s.get("name", "Student"), 22, True),
            self.label(f"Student code: {s.get('code', '')}"),
            self.label(f"Grade: {s.get('grade', 8)}"),
            self.label(f"XP: {s.get('xp', 0)}"),
            self.label(f"Level: {s.get('level', 1)}"),
            self.label(f"Questions today: {s.get('today_done', 0)}/{s.get('daily_goal', 20)}"),
            self.label(f"Papers generated: {len(s.get('papers', []))}"),
        ]
        self.set_content("Profile", children, back=True)

    def show_settings(self):
        self.set_content("Settings", [
            self.label("Learnly Grade 8 • Offline mode", 18, True),
            self.label("No network connection is required by the learning engine."),
            self.label("Developer mode is intended for testing only."),
            self.button("Back to Home", lambda *_: self.show_home()),
        ], back=True)


def main():
    return Learnly("Learnly", "org.learnly.grade8")


if __name__ == "__main__":
    main().main_loop()
