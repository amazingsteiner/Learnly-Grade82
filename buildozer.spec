[app]

# Learnly Grade 8 — Offline Kivy V1

title = Learnly Grade 8
package.name = learnlygrade8
package.domain = org.learnly

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0.0
orientation = portrait
fullscreen = 0

# Keep the Android dependency set minimal for the current Kivy application.
requirements = python3,kivy==2.3.1

# ARM Android devices.
android.archs = arm64-v8a,armeabi-v7a

# Let Buildozer manage the Android SDK/NDK under ~/.buildozer.
# Do not hard-code runner-specific SDK/NDK paths.
android.api = 35
android.minapi = 23

# Keep the application offline.
# No INTERNET permission is required by the Learnly V1 engine.
android.allow_backup = 1
android.debuggable = 1

presplash.filename =

[buildozer]
log_level = 2
warn_on_root = 1
