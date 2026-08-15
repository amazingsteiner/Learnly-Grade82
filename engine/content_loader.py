import json
import os
import sys
from pathlib import Path
from functools import lru_cache


def _find_content_dir():
    """Search several plausible roots so this keeps working even if the
    working directory or packaging layout differs (Pydroid, buildozer APK, desktop)."""
    candidates = []
    here = Path(__file__).resolve()
    candidates.append(here.parents[1] / "content" / "grade8")          # normal layout
    candidates.append(Path.cwd() / "content" / "grade8")               # run from project root
    if sys.path and sys.path[0]:
        candidates.append(Path(sys.path[0]) / "content" / "grade8")    # buildozer/APK entrypoint dir
    candidates.append(Path(os.path.abspath(".")) / "content" / "grade8")

    for c in candidates:
        if c.exists() and (c / "curriculum.json").exists():
            return c

    # last resort: walk up from this file looking for a 'content/grade8' folder anywhere nearby
    for parent in here.parents:
        guess = parent / "content" / "grade8"
        if guess.exists() and (guess / "curriculum.json").exists():
            return guess

    return candidates[0]  # will simply fail loudly later if truly missing


CONTENT_DIR = _find_content_dir()


@lru_cache(maxsize=1)
def load_curriculum():
    path = CONTENT_DIR / "curriculum.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print("Learnly: failed to parse curriculum.json:", e)
    return {}


@lru_cache(maxsize=32)
def load_topic_notes(topic_id):
    path = CONTENT_DIR / "topics" / f"{topic_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Learnly: failed to parse {topic_id}.json:", e)
    return None


def all_topics():
    return load_curriculum().get("topics", [])


def topic_name(topic_id):
    for t in all_topics():
        if t["id"] == topic_id:
            return t["name"]
    return topic_id.replace("_", " ").title()


def topic_icon(topic_id):
    for t in all_topics():
        if t["id"] == topic_id:
            return t.get("icon", "📘")
    return "📘"


def topics_for_term(term):
    return [t for t in all_topics() if t.get("term") == int(term)]


def content_status():
    """Diagnostic helper - screens can show this if notes ever fail to load."""
    return {
        "content_dir": str(CONTENT_DIR),
        "exists": CONTENT_DIR.exists(),
        "curriculum_found": (CONTENT_DIR / "curriculum.json").exists(),
        "topic_count": len(all_topics())
    }
