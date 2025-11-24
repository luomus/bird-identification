from pathlib import Path
from typing import List, Optional, Tuple, Union
import sys
import os
import librosa
import numpy as np
from PySide6.QtWidgets import QMessageBox, QWidget

def load_audio(file_path: str, sample_rate: Optional[str] = 24000) -> Tuple[np.ndarray, Union[int, float]]:
    y, sr = librosa.load(file_path, sr=sample_rate)
    if len(y) == 0:
        raise ValueError("Invalid audio file")
    return y, sr

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

def get_analyze_process() -> Tuple[str, List[str]]:
    if not getattr(sys, "frozen", False):
        return sys.executable, ["analyze_process.py"]

    file_name = "birdIdentifierAnalyze"

    if sys.platform == "win32":
        file_name += ".exe"

    return os.path.join(os.path.dirname(sys.executable), file_name), []
