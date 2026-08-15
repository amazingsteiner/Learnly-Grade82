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

# Kivy is handled by python-for-android's maintained recipe.
requirements = python3,kivy==2.3.1

# ARM Android devices.
android.archs = arm64-v8a,armeabi-v7a

# Android versions.
android.api = 35
android.minapi = 23

# GitHub Actions pre-installs these paths. Buildozer must reuse them
# instead of creating a second SDK under ~/.buildozer.
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/28.2.13676358

# Keep the application offline.
# No INTERNET permission is required by the Learnly V1 engine.
android.allow_backup = 1
android.debuggable = 1

presplash.filename =

[buildozer]
log_level = 2
warn_on_root = 1
