from pathlib import Path
from typing import List, Optional, Tuple, Union
import sys
import os
import librosa
import numpy as np

def load_audio(file_path: str, sr: Optional[float] = 24000, mono: Optional[bool] = None, offset: Optional[float] = None, duration: Optional[float] = None) -> Tuple[np.ndarray, Union[int, float]]:
    y, sr = librosa.load(file_path, sr=sr, mono=mono, offset=offset, duration=duration)
    if len(y) == 0:
        raise ValueError("Failed to load audio")
    return y, sr

def get_duration(file_path: str) -> float:
    duration = librosa.get_duration(path=file_path)
    if duration == 0:
        raise ValueError("Failed to load audio")
    return duration

def get_sample_rate(file_path: str) -> float:
    sample_rate = librosa.get_samplerate(file_path)
    if sample_rate == 0:
        raise ValueError("Failed to load audio")
    return sample_rate

def is_audio_file(file_name: str) -> bool:
    return file_name.lower().endswith((".wav", ".mp3", ".flac"))

def get_result_file_name(input_file_path: str, model_name: str) -> str:
    return "{}.{}.results.csv".format(Path(input_file_path).stem, model_name)

def get_default_model_path(model_name: str) -> Path:
    return get_default_models_folder_path() / model_name

def get_custom_model_path(model_name: str) -> Path:
    return get_custom_models_folder_path() / model_name

def get_available_models(model_type: Optional[str] = None) -> List[Path]:
    default_models = get_default_models_folder_path()
    custom_models = get_custom_models_folder_path()

    result = []

    if not model_type or model_type == "default":
        result += [d for d in default_models.iterdir() if d.is_dir()]
    if (not model_type or model_type == "custom") and custom_models.exists():
        result += [d for d in custom_models.iterdir() if d.is_dir()]

    return result

def get_default_models_folder_path():
    bundle_dir = Path(__file__).parent.parent

    return Path.cwd() / bundle_dir / "models"

def get_custom_models_folder_path() -> Path:
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            return Path(os.getenv("LOCALAPPDATA")) / "Bird Identifier" / "models"
        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "Bird Identifier" / "models"

    bundle_dir = Path(__file__).parent.parent

    return Path.cwd() / bundle_dir / "custom_models"

def get_analyze_process() -> Tuple[str, List[str]]:
    if not getattr(sys, "frozen", False):
        return sys.executable, ["analyze_process.py"]

    file_name = "birdIdentifierAnalyze"

    if sys.platform == "win32":
        file_name += ".exe"

    return os.path.join(os.path.dirname(sys.executable), file_name), []
