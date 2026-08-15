import sys
from pathlib import Path

# ============================================================
# LEARNLY — GRADE 8 MATHEMATICS
# Auto-locate project folder (works from Pydroid 3 or desktop)
# ============================================================


def find_learnly_folder():
    here = Path(__file__).resolve().parent
    possible_locations = [
        here,
        Path("/storage/emulated/0/Download/Learnly"),
        Path("/storage/emulated/0/Documents/Learnly"),
        Path("/storage/emulated/0/Learnly"),
        Path("/sdcard/Download/Learnly"),
        Path("/sdcard/Learnly"),
    ]
    for folder in possible_locations:
        if (folder.exists() and (folder / "engine").exists()
                and (folder / "screens").exists() and (folder / "ui").exists()):
            return folder
    return here  # fall back to the folder main.py lives in


LEARNLY_ROOT = find_learnly_folder()

if str(LEARNLY_ROOT) not in sys.path:
    sys.path.insert(0, str(LEARNLY_ROOT))


from PySide6.QtWidgets import QApplication
from engine.app import LearnlyApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Learnly")

    window = LearnlyApp()
    window.show()

    sys.exit(app.exec())
