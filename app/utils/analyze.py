import os
from pathlib import Path
from typing import Any, Tuple, Union, Callable

import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import tempfile
import math
from PySide6.QtCore import Signal

from utils.utils import is_audio_file, get_model_file_path
from scripts.classifier import Classifier
from scripts.run_model import process_audio_segment

MODEL_PATH = get_model_file_path("model_v3_5.h5")
BIRDNET_MODEL_PATH = get_model_file_path("BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite")
TFLITE_THREADS = 1
CLIP_DURATION = 3.0
audio_classifier = Classifier(
    path_to_mlk_model=MODEL_PATH,
    path_to_birdnet_model=BIRDNET_MODEL_PATH,
    sr=48000,
    clip_dur=CLIP_DURATION,
    TFLITE_THREADS=TFLITE_THREADS,
    offset=0,
    dur=0
)

def load_audio(file_path: str) -> Tuple[np.ndarray, Union[int, float]]:
    return librosa.load(file_path, sr=None)

def analyze_single_file(audio_data: Tuple[np.ndarray, Union[int, float]], progress_callback: Signal, **kwargs: dict[str, Any]) -> pd.DataFrame:
    def on_progress(data: dict[str, Any]) -> None:
        progress_callback.emit(data)

    params = _load_default_params()

    return _analyze(audio_data, on_progress, **{**params, **kwargs})

def analyze_multiple_files(input_folder_path: str, output_folder_path: str, progress_callback: Signal, **kwargs: dict[str, Any]):
    current_file = 0
    total_files = 0

    def on_progress(data: dict[str, Any]) -> None:
        data["file"] = current_file + 1
        data["total_files"] = total_files
        progress_callback.emit(data)

    params = _load_default_params()

    file_paths = []

    for (dirpath, dirnames, file_names) in os.walk(input_folder_path):
        for f in file_names:
            if is_audio_file(f):
                file_paths.append(os.path.join(dirpath, f))

    total_files = len(file_paths)

    for current_file, file_path in enumerate(file_paths):
        progress_callback.emit({"file": current_file + 1, "total_files": total_files})
        audio_data = load_audio(file_path)
        results = _analyze(audio_data, on_progress, **{**params, **kwargs})
        csv_path = os.path.join(output_folder_path, Path(file_path).stem + ".csv")
        results.to_csv(csv_path, index=False)

def _load_default_params() -> dict[str, Any]:
    return {
        "calibration_params": np.load(get_model_file_path("Pred_adjustment/calibration_params.npy")),
        "threshold": 0.6,
        "include_sdm": False,
        "include_noise": False,
        "migration_params": np.load(get_model_file_path("Pred_adjustment/migration_params.npy")),
        "lat": None,
        "lon": None,
        "day_of_year": None,
        "species_name_list": pd.read_csv(get_model_file_path("classes.csv")),
        "start_time": 0,
        "overlap": 0.5
    }

def _analyze(data: Tuple[np.ndarray, Union[int, float]], on_progress: Callable[[dict[str, Any]], Any], **kwargs: dict[str, Any]) -> pd.DataFrame:
    all_results = pd.DataFrame()

    audio_data, sr = data
    chunk_size = 600

    with tempfile.TemporaryDirectory() as temp_dir:
        chunk_size = chunk_size * sr

        for i in range(0, len(audio_data), chunk_size):
            on_progress({
                "chunk": int(i / chunk_size) + 1,
                "total_chunks": math.ceil(len(audio_data) / chunk_size),
            })

            chunk = audio_data[i:i + chunk_size]
            if len(chunk) == 0:
                continue

            temp_file_path = os.path.join(temp_dir, f"chunk_{i}.wav")
            sf.write(temp_file_path, chunk, sr)

            results_df = process_audio_segment(
                temp_file_path,
                audio_classifier,
                **kwargs
            )

            if not results_df.empty:
                all_results = pd.concat([all_results, results_df])

    return all_results
