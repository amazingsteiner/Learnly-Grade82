# Learnly Grade 8 — Kivy Offline V1

This is the Kivy rewrite of the supplied Learnly Grade 8 project.

## What changed
- Removed the PySide6 UI layer.
- Replaced the Qt timer with Kivy Clock.
- Preserved the existing pure-Python learning engines and Grade 8 content.
- Added a Kivy-native offline UI.
- Preserved the existing local JSON persistence model for student/paper data.
- Added the offline credit wallet and transaction ledger.
- Added Developer Mode with simulated credit purchases for Pydroid testing.
- Added a Buildozer configuration for Android APK generation.

## Run in Pydroid 3
From the project directory:

    pip install kivy
    python main.py

## Developer Mode
Settings → Enable Developer Mode → code:

    DEV-2026

This is a local simulation only. No payment gateway is contacted.

## Build APK
On Linux/WSL/Cloud build machine:

    pip install buildozer
    buildozer android debug

The APK will be placed in `bin/`.

## Offline architecture

Content → Question Engine → Adaptive/Mastery → Paper Engine → Local Student Data

No cloud API is required for V1.
