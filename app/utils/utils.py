from pathlib import Path
import os
from PySide6.QtWidgets import QMessageBox, QWidget

def is_audio_file(file_name: str) -> bool:
    return file_name.lower().endswith((".wav", ".mp3", ".flac"))

def show_alert(parent: QWidget, msg: str):
    dlg = QMessageBox(parent)
    dlg.setIcon(QMessageBox.Icon.Warning)
    dlg.setWindowTitle("Alert")
    dlg.setText(msg)
    dlg.show()

def get_model_file_path(file_name: str) -> str:
    if os.environ.get("LOCAL") == "true":
        return os.path.join("..", "models", file_name)

    bundle_dir = Path(__file__).parent.parent
    return str(Path.cwd() / bundle_dir / "models" / file_name)
