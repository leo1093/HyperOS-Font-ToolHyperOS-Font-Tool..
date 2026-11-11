# HyperOS Font Tool — prototype

A Windows desktop prototype with a dark developer-tool interface.

## What works
- Select `adb.exe` or use ADB from PATH.
- Run `adb devices` and detect an authorized USB-connected Android phone.
- Read manufacturer, model, Android version, and build ID.
- Import `.ttf` / `.otf` files and preview them in the app.

## Important limitation
This prototype DOES NOT install fonts on the phone. USB debugging does not automatically grant permission to replace Android system fonts. HyperOS font installation depends on the exact OS build and supported Xiaomi theme/overlay mechanisms. The install button is deliberately disabled until a safe, verified method for the target build is established.

## Requirements
- Windows 10/11
- Python 3.10+
- Android Platform Tools (ADB): https://developer.android.com/tools/releases/platform-tools
- On the phone: enable Developer options and USB debugging, connect by USB, unlock the phone, and accept the RSA authorization prompt.

## Run from source
1. Install Python.
2. Open a terminal in this folder.
3. Run: `py -m pip install -r requirements.txt`
4. Run: `py main.py`

## Build a Windows EXE
Run `build.bat`. The executable will be created in `dist\HyperOSFontTool.exe`.

To bundle ADB, create a `platform-tools` folder beside `main.py` and place `adb.exe` plus its required DLL files in it before building.

## Safety
The app only runs read-only ADB diagnostic commands. It does not modify the phone.

build by leo.bonnin
