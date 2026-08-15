LEARNLY — GRADE 8 MATHEMATICS + NATURAL SCIENCES (CAPS)
=========================================================

RUN
---
Desktop:  pip install PySide6   then   python main.py
Pydroid 3 (Android): open main.py and press ▶.

WHAT'S NEW IN THIS UPDATE
--------------------------
✔ FIXED: answer checking was too strict (rejected correct Algebra/algebraic-
  equations answers). Now uses engine/answer_check.py — a lenient comparator
  that handles spacing, "x=5" prefixes, fractions vs decimals, negative
  signs, coordinate pairs, and exponent-vs-evaluated-number answers.
✔ NEW TOPIC: Number Sense (Term 1) — basic addition/subtraction/
  multiplication/division with real strategies: number line jumps, making
  10, compensation, friendly-number tricks (×5/×25/×50/×9), doubling &
  halving, and basic division as inverse multiplication.
✔ FIXED: Question papers and the Maths Labs now render actual PNG IMAGES
  (via ui/render.py, drawn with QPainter onto a QPixmap and shown in a
  QLabel) instead of relying on live custom-paint widgets inside a scroll
  area — this is what was causing "glitchy" rendering. Paper Viewer embeds
  a diagram image per question where relevant, and "EXPORT AS IMAGE" now
  saves the WHOLE paper + memo as one composited PNG.
✔ DEEPER Data Handling Lab: grouped frequency table with class intervals
  and cumulative frequency, five-number summary, IQR-based outlier
  detection, plus a Histogram chart option — all still rendered as images.
✔ SHARPER hints: every hint across the question engine now references the
  actual numbers in that specific question instead of a generic method
  description.
✔ FIXED: "Notes not working" — content_loader.py now searches several
  plausible root folders (handles different working directories/packaging
  layouts) instead of relying on a single hardcoded path, and the topic
  screen shows a diagnostic message with the exact folder it looked in if
  content is ever genuinely missing, instead of failing silently.
✔ FIXED: Question Paper term selector — was reading the term from combo-box
  TEXT, which is fragile; now uses itemData (a real stored integer), so the
  generated paper always reflects the term you actually selected.
✔ NEW SUBJECT: Natural Sciences — Matter & Materials, Life & Living,
  Energy & Change, Planet Earth & Beyond, each with real CAPS-aligned notes
  and a code-generated diagram (states of matter, food chain, simple
  circuit, water cycle) — no external image files, so nothing to break or
  any copyright risk.
✔ NEW: Definitions Quiz mode — multiple-choice quiz built automatically
  from the key_vocabulary in every Maths AND Natural Sciences topic.
  Accessible from Home, Labs, and directly from any topic's notes screen.
✔ FIXED: Practice's topic checklist ("tick subject") text/tickboxes were
  too small — now uses a 14pt font and 26×26px checkboxes with more
  padding per row.

RUNNING INTO AN APK BUILD ISSUE?
----------------------------------
See learnly_to_apk.py (separate file) — it pushes this project to GitHub
via a fine-grained token and lets GitHub Actions build the APK. Note that
Buildozer/python-for-android's Android toolchain is built mainly for Kivy;
PySide6 doesn't have an officially maintained build recipe, so the Android
build step may still need custom work even though the "no git" issue is
now fixed in the workflow.

ARCHITECTURE
------------
main.py
engine/    app.py, question_engine.py, adaptive.py, mastery.py,
           paper_engine.py, timer_engine.py, content_loader.py,
           data_engine.py, geometry_engine.py, probability_engine.py,
           answer_check.py, science_engine.py, quiz_engine.py
screens/   login, home, learn, topic_detail, practice, practice_session,
           papers, paper_viewer, profile, settings, tutor, labs,
           geometry_lab, data_lab, probability_lab, mental_maths,
           science_learn, science_topic_detail, quiz_mode
ui/        theme_manager.py, widgets.py, render.py (image-based diagrams
           and charts), geometry_canvas.py (interactive lab canvas)
content/grade8/         curriculum.json, topics/*.json (14 Maths topics)
content/grade8/science/  curriculum.json, 4 Natural Sciences topic files
data/      students/, papers/, exports/  (auto-created, project-relative)

STUDENT LOGIN
-------------
Any student code creates/loads a local Grade 8 profile automatically.

TUTOR ACCESS CODE
------------------
children of the sun
(Prototype-level access control — not production authentication.)
