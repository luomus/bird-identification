import json
import os
from math import ceil
from threading import Event
from pathlib import Path
from typing import Any, Tuple, Union, Generator, Optional

import numpy as np
import pandas as pd
import librosa
from PySide6.QtCore import Signal

from scripts import functions
from functions.utils import is_audio_file, get_data_folder_path, get_model_folder_path
from scripts.classifier import Classifier

BIRDNET_MODEL_PATH = str(get_data_folder_path() / "BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite")
TFLITE_THREADS = 1
CLIP_DURATION = 3.0


def load_audio(file_path: str, sample_rate: Optional[str] = 24000) -> Tuple[np.ndarray, Union[int, float]]:
    y, sr = librosa.load(file_path, sr=sample_rate)
    if len(y) == 0:
        raise ValueError("Invalid audio file")
    return y, sr

def analyze_single_file(file_path: str, model_folder: str, threshold: float, overlap: float, progress_callback: Signal, cancel_requested: Event) -> pd.DataFrame:
    results = pd.DataFrame()

    model_path, classes, calibration_params = _get_model_data(model_folder)

    classifier = Classifier(
        path_to_mlk_model=model_path,
        path_to_birdnet_model=BIRDNET_MODEL_PATH,
        sr=48000,
        clip_dur=CLIP_DURATION,
        TFLITE_THREADS=TFLITE_THREADS,
    )

    for offset, chunk_size, total_duration in _audio_to_chunks(file_path):
        if cancel_requested.is_set():
            raise ValueError("Cancel requested")

        progress_callback.emit({
            "chunk": int(offset / chunk_size) + 1,
            "total_chunks": ceil(total_duration / chunk_size),
        })

        results = _add_results_for_chunk(
            file_path, classifier, classes, calibration_params, threshold, overlap, offset, chunk_size, results
        )

    results = _rename_result_columns(results)

    return results

def analyze_multiple_files(input_folder_path: str, output_folder_path: str, model_folder: str, threshold: float, overlap: float, progress_callback: Signal, cancel_requested: Event):
    successes = 0
    errors = 0

    model_path, classes, calibration_params = _get_model_data(model_folder)

    classifier = Classifier(
        path_to_mlk_model=model_path,
        path_to_birdnet_model=BIRDNET_MODEL_PATH,
        sr=48000,
        clip_dur=CLIP_DURATION,
        TFLITE_THREADS=TFLITE_THREADS
    )

    file_paths = []

    for (dirpath, dirnames, file_names) in os.walk(input_folder_path):
        for f in file_names:
            if is_audio_file(f):
                file_paths.append(os.path.join(dirpath, f))

    total_files = len(file_paths)

    for file_idx, file_path in enumerate(file_paths):
        if cancel_requested.is_set():
            raise ValueError("Cancel requested")

        progress_data = {"file": file_idx + 1, "total_files": total_files}
        progress_callback.emit(progress_data)

        try:
            results = pd.DataFrame()

            for offset, chunk_size, total_duration in _audio_to_chunks(file_path):
                if cancel_requested.is_set():
                    raise ValueError("Cancel requested")

                progress_callback.emit({**progress_data, "chunk": int(offset / chunk_size) + 1, "total_chunks": ceil(total_duration / chunk_size)})

                results = _add_results_for_chunk(
                    file_path, classifier, classes, calibration_params, threshold, overlap, offset, chunk_size, results
                )

            results = _rename_result_columns(results)

            result_file_path = _get_result_file_path(file_path, input_folder_path, output_folder_path)

            os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
            results.to_csv(result_file_path, index=False)

            successes += 1
        except Exception:
            errors += 1
            continue

    return {
        "successes": successes,
        "errors": errors
    }

def _get_model_data(model_folder: str) -> (str, pd.DataFrame, Optional[np.ndarray]):
    model_folder_path = get_model_folder_path() / model_folder
    metadata_path = model_folder_path / "metadata.json"

    with open(metadata_path, "r") as json_data:
        metadata = json.load(json_data)

    model_path = str(model_folder_path / metadata["model_file"])
    classes = pd.read_csv(model_folder_path / metadata["classes_file"])

    if "calibration_file" in metadata:
        calibration_params = np.load(model_folder_path / metadata["calibration_file"])

    return (model_path, classes, calibration_params)

def _get_model_file_paths(model_folder: str) -> dict[str, str]:
    model_path = get_model_folder_path() / model_folder
    metadata_path = model_path / "metadata.json"

    with open(metadata_path, "r") as json_data:
        metadata = json.load(json_data)

    result = {
        "model": model_path / metadata["model_file"],
        "classes": model_path / metadata["classes_file"],
    }

    if "calibration_file" in metadata:
        result["calibration"] = model_path / metadata["calibration_file"]

    return result

def _load_default_params(model_file_paths: dict[str, str]) -> dict[str, Any]:
    calibration_params = None

    calibration_params_path = model_file_paths["calibration"] if "calibration" in model_file_paths else None
    if calibration_params_path is not None:
        calibration_params = np.load(calibration_params_path)

    return {
        "calibration_params": calibration_params,
        "threshold": 0.6,
        "include_sdm": False,
        "include_noise": False,
        "migration_params": None,
        "lat": None,
        "lon": None,
        "day_of_year": None,
        "species_name_list": pd.read_csv(model_file_paths["classes"]),
        "start_time": 0,
        "overlap": 0.5
    }

def _audio_to_chunks(file_path: str, chunk_size: int = 600) -> Generator[tuple[int, int, float], None, None]:
    duration = librosa.get_duration(path=file_path)
    offset = 0

    while offset < duration:
        yield offset, chunk_size, duration
        offset += chunk_size

def _add_results_for_chunk(
        file_path: str,
        classifier: Classifier,
        classes: pd.DataFrame,
        calibration_params: Optional[np.ndarray],
        threshold: float,
        overlap: float,
        offset: int,
        duration: int,
        all_results: pd.DataFrame
):
    df = _analyze(file_path, classifier, classes, calibration_params, threshold, overlap, offset, duration)

    if not df.empty:
        all_results = pd.concat([all_results, df])

    return all_results

def _analyze(
        file_path: str,
        classifier: Classifier,
        classes: pd.DataFrame,
        calibration_params: Optional[np.ndarray],
        threshold: float,
        overlap: float,
        offset: int,
        duration: int
):
    species_predictions, detection_timestamps = classifier.classify(
        file_path,
        overlap=overlap,
        max_pred=False,
        offset=offset,
        duration=duration
    )

    if len(species_predictions) == 0:
        return pd.DataFrame()

    detection_timestamps += offset

    if calibration_params is not None:
        for i in range(len(species_predictions)):
            species_predictions[i, :] = functions.calibrate(
                species_predictions[i, :],
                calibration_params
            )

    species_predictions, species_class_indices, detection_timestamps = functions.threshold_filter(
        species_predictions,
        detection_timestamps,
        threshold
    )

    return functions.predictions_to_dataframe(
        species_predictions,
        species_class_indices,
        detection_timestamps,
        classes,
        classifier.clip_dur
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
