LEARNLY GRADE 8 - ANDROID BUILD

This project is the offline Kivy V1 of Learnly.

APK pipeline:
    Pydroid 3
        |
        | GitHub REST API
        v
    GitHub repository
        |
        | GitHub Actions
        v
    Buildozer
        |
        v
    python-for-android
        |
        v
    Learnly Grade 8 APK

The generated application is offline.

The GitHub connection is only used to compile the APK.

For a production release:
- disable Developer Mode
- review permissions
- configure signing
- build a release APK/AAB
- test on multiple Android devices
