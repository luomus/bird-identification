import pandas as pd
import numpy as np
import os
import gc
import functions

import librosa
import soundfile as sf
import tempfile

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


def process_audio_segment(
    segment_path: str,
    classifier,
    calibration_params: np.ndarray,
    threshold: float,
    include_sdm: bool,
    include_noise: bool,
    migration_params: np.ndarray,
    lat: float,
    lon: float,
    day_of_year: int,
    species_name_list: pd.DataFrame,
    start_time: float
) -> pd.DataFrame:
    """Process an audio segment and return predictions as a DataFrame.
    
    Args:
        segment_path: Path to audio segment file
        classifier: Audio classifier instance
        calibration_params: Calibration parameters
        threshold: Confidence threshold
        include_sdm: Whether to apply species distribution model
        include_noise: Whether to include noise detections
        migration_params: Migration parameters for SDM
        lat: Latitude
        lon: Longitude
        day_of_year: Day of year
        species_name_list: DataFrame with species names
        start_time: Start time of segment in original file
        
    Returns:
        DataFrame with columns: start_time, end_time, scientific_name, common_name, confidence
    """
    # Get predictions from classifier
    species_predictions, detection_timestamps = classifier.classify(segment_path, max_pred=False)
    
    if len(species_predictions) == 0:
        return pd.DataFrame()
    
    # Convert to numpy arrays
    species_predictions = np.array(species_predictions)
    detection_timestamps = np.array(detection_timestamps)
    
    # Adjust timestamps relative to original file
    detection_timestamps += start_time
    
    # Calibrate predictions
    for i in range(len(species_predictions)):
        species_predictions[i, :] = functions.calibrate(
            species_predictions[i, :],
            calibration_params
        )
    
    # Apply threshold filter
    species_predictions, species_class_indices, detection_timestamps = functions.threshold_filter(
        species_predictions,
        detection_timestamps,
        threshold
    )
    
    # Apply species distribution model adjustment
    if include_sdm and len(species_predictions) > 0:
        species_predictions = functions.adjust(
            species_predictions,
            species_class_indices,
            migration_params,
            lat,
            lon,
            day_of_year
        )
    
    # Build DataFrame with results
    results = []
    for i in range(len(species_predictions)):
        # Skip noise/human detections if configured
        if species_class_indices[i] <= 1 and not include_noise:
            continue
            
        results.append({
            'start_time': detection_timestamps[i],
            'end_time': detection_timestamps[i] + classifier.clip_dur,
            'scientific_name': species_name_list['luomus_name'].iloc[species_class_indices[i]],
            'common_name': species_name_list['common_name'].iloc[species_class_indices[i]],
            'confidence': round(float(species_predictions[i]), 4)
        })
    
    return pd.DataFrame(results)


def write_inference_metadata(output_path: str, metadata_dict: Dict[str, Any]) -> None:
    """Write model inference metadata to a YAML file with timestamp in the filename.

    Args:
        output_path: Directory path where the metadata file will be saved.
        metadata_dict: Dictionary containing metadata key-value pairs to be written.
    """
    from datetime import datetime
    date_string = datetime.now().strftime("%Y-%m-%d_%H-%M")
    with open(f"{output_path}/inference_{date_string}.yaml", "w") as f:
        for key, value in metadata_dict.items():
            f.write(f"{key}: {value}\n")


def analyze_directory(input_path, parameters):
    metadata = parameters["metadata"]
    print("Metadata loaded: ", metadata)
    lat = metadata["lat"]
    lon = metadata["lon"]
    day_of_year = metadata["day_of_year"]

    from classifier import Classifier
    from tensorflow import keras

    print(f"\nAnalyzing audio files at {input_path}")

    # Parameters
    THRESHOLD = parameters["threshold"]
    INCLUDE_NOISE = parameters["noise"]
    INCLUDE_SDM = parameters["sdm"]
    SKIP_IF_OUTPUT_EXISTS = parameters["skip"]

    print("Parameters: ", parameters)

    # Standard settings
    output_path = input_path
    MODEL_PATH = "../models/model_v3_5.keras"
    TFLITE_THREADS = 1

    # Load classification model
    # TFLITE_THREADS can be as high as number of CPUs available, the rest of the parameters should not be changed
    CLIP_DURATION = 3.0
    audio_classifier = Classifier(path_to_mlk_model=MODEL_PATH, sr=48000, clip_dur=CLIP_DURATION, TFLITE_THREADS=TFLITE_THREADS, offset=0, dur=0)

    # Load species name list and post-processing tables for prediction calibration
    species_name_list = pd.read_csv("classes.csv")
    migration_parameters = np.load("Pred_adjustment/migration_params.npy")
    calibration_parameters = np.load("Pred_adjustment/calibration_params.npy")

    # Get list of files in input folder
    files = functions.get_audio_file_names(input_path)

    number_of_files = len(files)

    # As the model cannot handle long audio files, split them into segments of SEGMENT_LENGTH seconds
    SEGMENT_LENGTH = 600

    # Loop each audio file in input folder
    analyzed_files_count = 0
    skipped_files_count = 0
    read_day_of_year_from_audiofile = False
    for file_index, file_name in enumerate(files):
        try:
            file_path = f"{input_path}/{file_name}"
            output_file_path, output_file_exists = functions.make_output_file_path(output_path, file_name)

            if output_file_exists and SKIP_IF_OUTPUT_EXISTS:
                print(f"Skipping {file_path} because output file exists and skipping is enabled.")
                skipped_files_count += 1
                continue

            print(f"Loading file {file_path} ({file_index + 1} of {number_of_files})")

            # If filename contains a date, use that instead of the metadata date. Note that only pre-specified date formats are supported.
            day_of_year_from_file = functions.get_day_of_year_from_filename(file_name)
            if day_of_year_from_file is not None:
                day_of_year = day_of_year_from_file
                print(f"Day of year from filename: {day_of_year}")
                read_day_of_year_from_audiofile = True

            # Create an empty output file with header
            # Todo: Since this creates file before data is written into it, aborting the process will leave an empty file, which may cause subsequent analysis to be skipped. Instead write all output first into memory, and into file only after all data is ready.
            with open(output_file_path, "w") as output_file_writer:
                output_file_writer.write("Start (s),End (s),Scientific name,Common name,Confidence\n")

            # Load audio file
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            
            # Create temporary directory for segments
            with tempfile.TemporaryDirectory() as temp_dir:
                # Split into segments

                segment_count = int(duration) // SEGMENT_LENGTH + 1
                print(f"Splitting file into {segment_count} temporary segments of {SEGMENT_LENGTH} seconds")

                for start_time in range(0, int(duration), SEGMENT_LENGTH):
                    # Calculate end time for segment
                    end_time = min(start_time + SEGMENT_LENGTH, duration)
                    
                    # Convert time to samples
                    start_sample = int(start_time * sample_rate)
                    end_sample = int(end_time * sample_rate)
                    
                    # Extract segment
                    segment = audio_data[start_sample:end_sample]
                    
                    # Create temporary file for segment
                    temp_file_path = os.path.join(temp_dir, f"segment_{start_time}.wav")
                    sf.write(temp_file_path, segment, sample_rate)
                    
                    # Process audio segment and get predictions as DataFrame
                    predictions_df = process_audio_segment(
                        temp_file_path,
                        audio_classifier,
                        calibration_parameters,
                        THRESHOLD,
                        INCLUDE_SDM,
                        INCLUDE_NOISE,
                        migration_parameters,
                        lat,
                        lon,
                        day_of_year,
                        species_name_list,
                        start_time
                    )
                    
                    if not predictions_df.empty:
                        # Append results to output file
                        predictions_df.to_csv(output_file_path, mode='a', header=False, index=False)
                        print(f"Wrote predictions to {output_file_path}")
                    
                # After each file
                gc.collect()
                analyzed_files_count += 1

        # Handle exceptions
        except Exception as e: 
            print(f"Error: Error analyzing {file_name}!")
            print(f"Error details: {str(e)}")
            raise

    metadata_dict = {
        "day_of_year_from_metadata": metadata["day_of_year"],
        "read_day_of_year_from_audiofile": read_day_of_year_from_audiofile,
        "lat": lat,
        "lon": lon,
        "threshold": THRESHOLD,
        "include_noise": INCLUDE_NOISE,
        "include_sdm": INCLUDE_SDM,
        "skip_if_output_exists": SKIP_IF_OUTPUT_EXISTS,
        "model": MODEL_PATH,
        "skipped_files_count": skipped_files_count,
        "analyzed_files_count": analyzed_files_count
    }
    write_inference_metadata(output_path, metadata_dict)

    print("All files analyzed")
    return True
