import os
import sys
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame, QLineEdit, QMessageBox,
    QTextEdit, QProgressBar
)

APP_DIR = Path(__file__).resolve().parent

def find_adb():
    candidates = [
        APP_DIR / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb"),
        APP_DIR / "adb.exe",
        Path("adb.exe" if os.name == "nt" else "adb"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return "adb"

class FontTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HyperOS Font Tool")
        self.resize(940, 680)
        self.adb_path = find_adb()
        self.font_path = None
        self.font_id = -1
        self.setStyleSheet("""
            QWidget { background:#10141d; color:#e7edf7; font-family:'Segoe UI'; font-size:10pt; }
            QFrame#panel { background:#171e2b; border:1px solid #2a3548; border-radius:12px; }
            QLabel#muted { color:#91a0b7; }
            QLabel#title { font-size:23pt; font-weight:700; color:#f4f7ff; }
            QPushButton { background:#26364d; border:1px solid #3b506d; border-radius:8px; padding:10px 14px; }
            QPushButton:hover { background:#314763; }
            QPushButton:disabled { color:#758197; background:#202938; }
            QPushButton#primary { background:#3978d6; border-color:#5592ee; font-weight:600; }
            QLineEdit, QTextEdit { background:#0c1119; border:1px solid #2a3548; border-radius:7px; padding:8px; }
            QProgressBar { background:#0c1119; border:0; border-radius:5px; height:8px; }
            QProgressBar::chunk { background:#4e9bff; border-radius:5px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("HYPEROS FONT TOOL")
        title.setObjectName("title")
        subtitle = QLabel("ADB desktop utility  •  Font import & device diagnostics")
        subtitle.setObjectName("muted")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        self.status = QLabel("●  NOT CONNECTED")
        self.status.setStyleSheet("color:#f0b44d; font-weight:700;")
        header.addWidget(self.status, alignment=Qt.AlignVCenter)
        layout.addLayout(header)

        device_panel = self.panel()
        d = QVBoxLayout(device_panel)
        d.addWidget(self.heading("01  DEVICE CONNECTION"))
        row = QHBoxLayout()
        self.adb_edit = QLineEdit(self.adb_path)
        self.adb_edit.setPlaceholderText("Path to adb.exe (or 'adb' if on PATH)")
        browse_adb = QPushButton("Browse ADB")
        browse_adb.clicked.connect(self.pick_adb)
        detect = QPushButton("Detect device")
        detect.setObjectName("primary")
        detect.clicked.connect(self.detect_device)
        row.addWidget(self.adb_edit, 1)
        row.addWidget(browse_adb)
        row.addWidget(detect)
        d.addLayout(row)
        self.device_info = QLabel("Connect your phone by USB, enable USB debugging, then accept the authorization prompt.")
        self.device_info.setObjectName("muted")
        self.device_info.setWordWrap(True)
        d.addWidget(self.device_info)
        layout.addWidget(device_panel)

        font_panel = self.panel()
        f = QVBoxLayout(font_panel)
        f.addWidget(self.heading("02  CUSTOM FONT"))
        font_row = QHBoxLayout()
        self.font_name = QLabel("No font selected")
        self.font_name.setObjectName("muted")
        choose = QPushButton("Choose .TTF / .OTF")
        choose.clicked.connect(self.pick_font)
        font_row.addWidget(self.font_name, 1)
        font_row.addWidget(choose)
        f.addLayout(font_row)
        self.preview = QLabel("The quick brown fox jumps over the lazy dog\nAa Bb Cc 0123456789")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(125)
        self.preview.setStyleSheet("background:#0c1119; border:1px dashed #40516b; border-radius:9px; font-size:19pt;")
        f.addWidget(self.preview)
        layout.addWidget(font_panel)

        install_panel = self.panel()
        i = QVBoxLayout(install_panel)
        i.addWidget(self.heading("03  INSTALLATION STATUS"))
        note = QLabel(
            "Font installation is intentionally not enabled yet. ADB access alone does not grant permission "
            "to replace Android system fonts, and HyperOS versions use different restrictions. This build "
            "can detect the phone and preview fonts, but it will not claim to install a font when no "
            "verified HyperOS-compatible method is available."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        i.addWidget(note)
        self.install_button = QPushButton("Installation unavailable — compatibility not verified")
        self.install_button.setEnabled(False)
        i.addWidget(self.install_button)
        layout.addWidget(install_panel)

        log_panel = self.panel()
        log_layout = QVBoxLayout(log_panel)
        log_layout.addWidget(self.heading("ADB LOG"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(105)
        self.log.setPlainText("Ready. No commands have been run yet.")
        log_layout.addWidget(self.log)
        layout.addWidget(log_panel)

        footer = QLabel("No root  •  No Shizuku  •  Diagnostic prototype")
        footer.setObjectName("muted")
        layout.addWidget(footer)

    def panel(self):
        frame = QFrame()
        frame.setObjectName("panel")
        return frame

    def heading(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-weight:700; color:#8ebcff; letter-spacing:1px;")
        return label

    def write_log(self, text):
        self.log.append(text)

    def pick_adb(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ADB executable", "", "ADB executable (adb.exe);;All files (*)")
        if path:
            self.adb_edit.setText(path)
            self.adb_path = path

    def pick_font(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select a font", "", "Font files (*.ttf *.otf)")
        if not path:
            return
        self.font_path = path
        self.font_name.setText(Path(path).name)
        self.font_name.setStyleSheet("color:#e7edf7;")
        self.font_id = QFontDatabase.addApplicationFont(path)
        families = QFontDatabase.applicationFontFamilies(self.font_id) if self.font_id >= 0 else []
        if families:
            self.preview.setFont(QFont(families[0], 19))
            self.write_log(f"Loaded font preview: {families[0]} ({Path(path).name})")
        else:
            self.preview.setFont(QFont("Segoe UI", 19))
            self.write_log("Could not load this font for preview. Check that the file is a valid TTF/OTF.")
            QMessageBox.warning(self, "Font preview", "Windows/Qt could not load this font file.")

    def run_adb(self, args):
        adb = self.adb_edit.text().strip() or "adb"
        try:
            result = subprocess.run([adb, *args], capture_output=True, text=True, timeout=12, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            output = (result.stdout or result.stderr).strip()
            self.write_log(f"> adb {' '.join(args)}\n{output or '(no output)'}")
            return result.returncode, output
        except FileNotFoundError:
            self.write_log("ADB not found. Install Android Platform Tools or select adb.exe.")
            return 127, "ADB not found"
        except subprocess.TimeoutExpired:
            self.write_log("ADB command timed out.")
            return 124, "ADB timeout"

    def detect_device(self):
        code, output = self.run_adb(["devices"])
        lines = output.splitlines()
        devices = [line.split()[0] for line in lines[1:] if len(line.split()) >= 2 and line.split()[1] == "device"]
        unauthorized = any("unauthorized" in line for line in lines)
        if not devices:
            self.status.setText("●  NOT CONNECTED")
            self.status.setStyleSheet("color:#f0b44d; font-weight:700;")
            self.device_info.setText("No authorized device found. Check the USB cable, enable USB debugging and accept the RSA prompt on your phone." if not unauthorized else "Phone detected but not authorized. Unlock it and accept the USB debugging permission prompt.")
            return
        self.status.setText("●  CONNECTED")
        self.status.setStyleSheet("color:#65d69a; font-weight:700;")
        _, model = self.run_adb(["shell", "getprop", "ro.product.model"])
        _, android = self.run_adb(["shell", "getprop", "ro.build.version.release"])
        _, manufacturer = self.run_adb(["shell", "getprop", "ro.product.manufacturer"])
        _, build = self.run_adb(["shell", "getprop", "ro.build.display.id"])
        self.device_info.setText(f"{manufacturer} {model}  •  Android {android}  •  Build: {build}")
        self.write_log("Device detected. This is diagnostic only; no system settings were changed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FontTool()
    window.show()
    sys.exit(app.exec())