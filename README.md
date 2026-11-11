# HyperOS Font Tool v0.2

Windows prototype for Xiaomi/Redmi phones.

## Features
- Detect authorized Android phones over USB with ADB.
- Read model, Android version and build ID.
- Preview TTF/OTF files.
- Select TTF, OTF or MTZ files and transfer them to `/sdcard/Download/HyperOSFontTool/`.

## Important
This version transfers files only. It does NOT install or apply a font/theme. ADB copying to Downloads does not bypass Xiaomi's theme-engine checks or Android restrictions on `Android/data`. A compatible Xiaomi theme import/apply workflow is still required.

## Requirements
Windows 10/11, Python 3.10+, Android Platform Tools (ADB): https://developer.android.com/tools/releases/platform-tools
Enable USB debugging and authorize this PC on the phone.

## Run
`py -m pip install -r requirements.txt`
`py main.py`

## Build EXE
Run `build.bat`.
