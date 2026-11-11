@echo off
py -m pip install -r requirements.txt
py -m PyInstaller --noconfirm --onefile --windowed --name HyperOSFontTool main.py
pause
