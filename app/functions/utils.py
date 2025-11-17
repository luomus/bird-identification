from pathlib import Path
from typing import List

from PySide6.QtWidgets import QMessageBox, QWidget

def is_audio_file(file_name: str) -> bool:
    return file_name.lower().endswith((".wav", ".mp3", ".flac"))

def show_alert(parent: QWidget, msg: str):
    dlg = QMessageBox(parent)
    dlg.setIcon(QMessageBox.Icon.Warning)
    dlg.setWindowTitle("Alert")
    dlg.setText(msg)
    dlg.show()

def get_data_folder_path() -> Path:
    bundle_dir = Path(__file__).parent.parent

    return Path.cwd() / bundle_dir / "data"

def get_model_folder_path() -> Path:
    bundle_dir = Path(__file__).parent.parent

    return Path.cwd() / bundle_dir / "models"

def get_available_models() -> List[str]:
    models_path = get_model_folder_path()

    return [p.name for p in models_path.iterdir() if p.is_dir()]
