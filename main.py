import os, sys, subprocess
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame, QLineEdit, QMessageBox, QTextEdit

APP_DIR = Path(__file__).resolve().parent

def adb_default():
    for p in [APP_DIR/"platform-tools"/"adb.exe", APP_DIR/"adb.exe", Path("adb.exe")]:
        if p.is_file(): return str(p)
    return "adb"

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HyperOS Font Tool")
        self.resize(950, 700)
        self.file = None
        self.setStyleSheet("""
        QWidget{background:#10141d;color:#e7edf7;font-family:'Segoe UI';font-size:10pt}
        QFrame#panel{background:#171e2b;border:1px solid #2a3548;border-radius:12px}
        QLabel#muted{color:#91a0b7} QLabel#title{font-size:23pt;font-weight:700}
        QPushButton{background:#26364d;border:1px solid #3b506d;border-radius:8px;padding:10px}
        QPushButton:hover{background:#314763} QPushButton#primary{background:#3978d6;font-weight:600}
        QLineEdit,QTextEdit{background:#0c1119;border:1px solid #2a3548;border-radius:7px;padding:8px}
        """)
        w=QWidget(); self.setCentralWidget(w); l=QVBoxLayout(w); l.setContentsMargins(26,22,26,22); l.setSpacing(14)
        h=QHBoxLayout(); titles=QVBoxLayout()
        title=QLabel("HYPEROS FONT TOOL"); title.setObjectName("title")
        sub=QLabel("ADB desktop utility • Font/theme file transfer"); sub.setObjectName("muted")
        titles.addWidget(title); titles.addWidget(sub); h.addLayout(titles); h.addStretch()
        self.status=QLabel("● NOT CONNECTED"); self.status.setStyleSheet("color:#f0b44d;font-weight:700"); h.addWidget(self.status); l.addLayout(h)

        p=self.panel(); a=QVBoxLayout(p); a.addWidget(self.head("01  DEVICE CONNECTION"))
        r=QHBoxLayout(); self.adb=QLineEdit(adb_default()); b=QPushButton("Browse ADB"); b.clicked.connect(self.pick_adb)
        d=QPushButton("Detect device"); d.setObjectName("primary"); d.clicked.connect(self.detect)
        r.addWidget(self.adb,1); r.addWidget(b); r.addWidget(d); a.addLayout(r)
        self.device=QLabel("Connect your phone, enable USB debugging and accept the authorization prompt."); self.device.setObjectName("muted"); a.addWidget(self.device); l.addWidget(p)

        p=self.panel(); a=QVBoxLayout(p); a.addWidget(self.head("02  FONT / THEME FILE"))
        r=QHBoxLayout(); self.filename=QLabel("No file selected"); self.filename.setObjectName("muted")
        c=QPushButton("Choose .TTF / .OTF / .MTZ"); c.clicked.connect(self.pick_file); r.addWidget(self.filename,1); r.addWidget(c); a.addLayout(r)
        self.preview=QLabel("The quick brown fox jumps over the lazy dog\\nAa Bb Cc 0123456789"); self.preview.setAlignment(Qt.AlignCenter); self.preview.setMinimumHeight(100)
        self.preview.setStyleSheet("background:#0c1119;border:1px dashed #40516b;border-radius:9px;font-size:18pt"); a.addWidget(self.preview); l.addWidget(p)

        p=self.panel(); a=QVBoxLayout(p); a.addWidget(self.head("03  TRANSFER TO PHONE"))
        dest=QLabel("Destination: /sdcard/Download/HyperOSFontTool/"); dest.setObjectName("muted"); a.addWidget(dest)
        self.transfer=QPushButton("Transfer selected file to phone"); self.transfer.setObjectName("primary"); self.transfer.setEnabled(False); self.transfer.clicked.connect(self.push_file); a.addWidget(self.transfer)
        note=QLabel("Copies the file to shared Downloads using ADB. This does NOT install or apply the font. TTF/OTF still needs a compatible Xiaomi theme workflow; MTZ still needs a supported importer."); note.setObjectName("muted"); note.setWordWrap(True); a.addWidget(note); l.addWidget(p)

        p=self.panel(); a=QVBoxLayout(p); a.addWidget(self.head("ADB LOG")); self.log=QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(125); self.log.setPlainText("Ready."); a.addWidget(self.log); l.addWidget(p)
        foot=QLabel("No root • No Shizuku • ADB file-transfer prototype"); foot.setObjectName("muted"); l.addWidget(foot)

    def panel(self):
        p=QFrame(); p.setObjectName("panel"); return p
    def head(self,s):
        x=QLabel(s); x.setStyleSheet("font-weight:700;color:#8ebcff;letter-spacing:1px"); return x
    def logit(self,s): self.log.append(s)
    def cmd(self,args,timeout=30):
        try:
            q=subprocess.run([self.adb.text().strip() or "adb",*args],capture_output=True,text=True,timeout=timeout,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
            out=(q.stdout or q.stderr).strip(); self.logit("> adb "+" ".join(args)+"\\n"+(out or "(no output)")); return q.returncode,out
        except Exception as e:
            self.logit(str(e)); return 1,str(e)
    def pick_adb(self):
        p,_=QFileDialog.getOpenFileName(self,"Select adb.exe","","ADB executable (adb.exe)")
        if p:self.adb.setText(p)
    def pick_file(self):
        p,_=QFileDialog.getOpenFileName(self,"Select file","","Supported files (*.ttf *.otf *.mtz)")
        if not p:return
        self.file=p; self.filename.setText(Path(p).name); self.filename.setStyleSheet("color:#e7edf7")
        ext=Path(p).suffix.lower()
        if ext in (".ttf",".otf"):
            fid=QFontDatabase.addApplicationFont(p); fam=QFontDatabase.applicationFontFamilies(fid) if fid>=0 else []
            if fam:self.preview.setFont(QFont(fam[0],18))
            else:self.preview.setText("Font selected • preview unavailable")
        else:
            self.preview.setFont(QFont("Segoe UI",14)); self.preview.setText("MTZ theme selected\\nReady to transfer")
        self.transfer.setEnabled(self.status.text().startswith("● CONNECTED"))
    def detect(self):
        rc,out=self.cmd(["devices"])
        lines=out.splitlines(); dev=[x for x in lines[1:] if len(x.split())>1 and x.split()[1]=="device"]
        una="unauthorized" in out
        if not dev:
            self.status.setText("● NOT CONNECTED"); self.status.setStyleSheet("color:#f0b44d;font-weight:700")
            self.transfer.setEnabled(False); self.device.setText("Phone unauthorized. Unlock it and accept the USB debugging prompt." if una else "No authorized phone found. Check cable and USB debugging."); return
        self.status.setText("● CONNECTED"); self.status.setStyleSheet("color:#65d69a;font-weight:700")
        _,model=self.cmd(["shell","getprop","ro.product.model"]); _,android=self.cmd(["shell","getprop","ro.build.version.release"]); _,build=self.cmd(["shell","getprop","ro.build.display.id"])
        self.device.setText(f"{model} • Android {android} • Build {build}"); self.transfer.setEnabled(bool(self.file))
    def push_file(self):
        if not self.file:return
        folder="/sdcard/Download/HyperOSFontTool"
        rc,out=self.cmd(["shell","mkdir","-p",folder])
        if rc:
            QMessageBox.critical(self,"Transfer failed","Could not create destination folder."); return
        target=folder+"/"+Path(self.file).name
        rc,out=self.cmd(["push",self.file,target],120)
        if rc==0: QMessageBox.information(self,"Transfer complete",f"Copied to:\\n{target}\\n\\nThis is only a file transfer, not font installation.")
        else: QMessageBox.critical(self,"Transfer failed",out or "ADB push failed.")

if __name__=="__main__":
    app=QApplication(sys.argv); win=Main(); win.show(); sys.exit(app.exec())
