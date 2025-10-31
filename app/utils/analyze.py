import os
from pathlib import Path
from typing import Any, Tuple, Union, Generator

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
    y, sr = librosa.load(file_path, sr=None)
    if len(y) == 0:
        raise ValueError("Invalid audio file")
    return y, sr

def analyze_single_file(audio_data: Tuple[np.ndarray, Union[int, float]], progress_callback: Signal, **kwargs: dict[str, Any]) -> pd.DataFrame:
    results = pd.DataFrame()

    default_params = _load_default_params()
    params = {**default_params, **kwargs}

    for chunk_file, chunk_idx, total_chunks in _audio_to_chunks(audio_data[0], audio_data[1]):
        progress_callback.emit({
            "chunk": chunk_idx + 1,
            "total_chunks": total_chunks,
        })

        results = _add_results_for_chunk(chunk_file, results, **params)

    results = _rename_result_columns(results)

    return results

def analyze_multiple_files(input_folder_path: str, output_folder_path: str, progress_callback: Signal, **kwargs: dict[str, Any]):
    default_params = _load_default_params()
    params = {**default_params, **kwargs}

    file_paths = []

    for (dirpath, dirnames, file_names) in os.walk(input_folder_path):
        for f in file_names:
            if is_audio_file(f):
                file_paths.append(os.path.join(dirpath, f))

    total_files = len(file_paths)

    for file_idx, file_path in enumerate(file_paths):
        progress_data = {"file": file_idx + 1, "total_files": total_files}
        progress_callback.emit(progress_data)

        try:
            audio_data, sr = load_audio(file_path)

            results = pd.DataFrame()

            for chunk_file, chunk_idx, total_chunks in _audio_to_chunks(audio_data, sr):
                progress_callback.emit({**progress_data, "chunk": chunk_idx + 1, "total_chunks": total_chunks})

                results = _add_results_for_chunk(chunk_file, results, **params)

            results = _rename_result_columns(results)

            result_file_path = _get_result_file_path(file_path, input_folder_path, output_folder_path)

            os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
            results.to_csv(result_file_path, index=False)
        except Exception as e:
            continue

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

def _audio_to_chunks(audio_data: np.ndarray, sr: Union[int, float], chunk_size: int = 600) -> Generator[str, None, None]:
    chunk_size = chunk_size * sr
    total_chunks = math.ceil(len(audio_data) / chunk_size)

    with tempfile.TemporaryDirectory() as temp_dir:
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]

            temp_file_path = os.path.join(temp_dir, f"chunk_{i}.wav")
            sf.write(temp_file_path, chunk, sr)

            yield temp_file_path, int(i / chunk_size), total_chunks

def _add_results_for_chunk(file_path: str, all_results: pd.DataFrame, **kwargs: dict[str, Any]) -> pd.DataFrame:
    df = _analyze(file_path, **kwargs)

    if not df.empty:
        all_results = pd.concat([all_results, df])

    return all_results

def _analyze(file_path: str, **kwargs: dict[str, Any]) -> pd.DataFrame:
    return process_audio_segment(
        file_path,
        audio_classifier,
        **kwargs
    )

def _rename_result_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["Start (s)", "End (s)", "Scientific name", "Common name", "Confidence"]

    if not df.empty:
        df.columns = columns
        return df

    return pd.DataFrame(columns=columns)

def _get_result_file_path(file_path: str, input_folder_path: str, output_folder_path: str) -> str:
    dir_rel_path = os.path.relpath(os.path.dirname(file_path), input_folder_path)
    result_file_name = Path(file_path).stem + ".Muuttolinnut.results.csv"
    return os.path.join(output_folder_path, dir_rel_path, result_file_name)
