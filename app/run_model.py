import pandas as pd
import numpy as np
import os
import gc
import functions
import traceback

import librosa
import soundfile as sf
import tempfile

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


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


@dataclass
class AnalysisParameters:
    """Class to validate and store analysis parameters."""
    directory: str
    threshold: float = 0.5
    noise: bool = False
    sdm: bool = False
    skip: bool = False


    @staticmethod
    def validate_directory(directory: str) -> Tuple[Optional[str], Optional[str]]:
        """Validate directory path.
        Returns: (validated_path, error_message)"""

        if directory is None:
            return None, "Directory path cannot be empty"

        data_directory, error_message = functions.get_data_directory(directory)
        if error_message:
            return None, error_message

        return data_directory, None


    @staticmethod
    def validate_threshold(threshold: Any) -> Tuple[float, Optional[str]]:
        """Validate threshold value.
        Returns: (validated_value, warning_message)"""
        default_value = 0.5
        
        # Handle type conversion
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return default_value, f"Invalid threshold value '{threshold}', using default {default_value}"

        # Handle range validation
        if not (0 <= threshold <= 1):
            return default_value, f"Threshold must be between 0 and 1, using default {default_value}"
            
        return threshold, None


    @staticmethod
    def validate_boolean(value: Any, param_name: str) -> Tuple[bool, Optional[str]]:
        """Validate boolean parameters.
        Returns: (validated_value, warning_message)"""
        if isinstance(value, bool):
            return value, None
        
        return False, f"Invalid {param_name} value '{value}', using default False"


    @classmethod
    def create(cls, directory: str, threshold: Any = 0.5, 
               noise: Any = False, sdm: Any = False, 
               skip: Any = False) -> Tuple['AnalysisParameters', list[str]]:
        """Factory method to create and validate parameters.
        Returns: (parameters, warning_messages)"""
        warnings = []
        
        # Validate directory (required parameter)
        valid_dir, dir_error = cls.validate_directory(directory)
        if dir_error:
            raise ValueError(dir_error)
        
        # Validate threshold
        valid_threshold, thr_warning = cls.validate_threshold(threshold)
        if thr_warning:
            warnings.append(thr_warning)
            
        # Validate boolean parameters
        valid_noise, noise_warning = cls.validate_boolean(noise, "noise")
        if noise_warning:
            warnings.append(noise_warning)
            
        valid_sdm, sdm_warning = cls.validate_boolean(sdm, "sdm")
        if sdm_warning:
            warnings.append(sdm_warning)
            
        valid_skip, skip_warning = cls.validate_boolean(skip, "skip")
        if skip_warning:
            warnings.append(skip_warning)

        return cls(
            directory=valid_dir,
            threshold=valid_threshold,
            noise=valid_noise,
            sdm=valid_sdm,
            skip=valid_skip
        ), warnings


    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary format."""
        return {
            'threshold': self.threshold,
            'noise': self.noise,
            'sdm': self.sdm,
            'skip': self.skip
        }


def analyze_directory(input_path, parameters):
    # Read folder-specific metadata
    metadata = functions.read_metadata(input_path)
    if metadata is None:
        print(f"Error: Proper metadata file not found at {input_path}")
        return False
    
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
    MODEL_PATH = "models/model_v3_5.keras"
    TFLITE_THREADS = 1

    # Load classification model
    # TFLITE_THREADS can be as high as number of CPUs available, the rest of the parameters should not be changed
    CLIP_DURATION = 3.0
    audio_classifier = Classifier(path_to_model=MODEL_PATH, sr=48000, clip_dur=CLIP_DURATION, TFLITE_THREADS=TFLITE_THREADS, offset=0, dur=0)

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
    read_day_of_year_from_file = False
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
                read_day_of_year_from_file = True

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
                    
                    # Predict species for segment
                    # Todo: this fails if max_pred is True
                    species_predictions, detection_timestamps = audio_classifier.classify(temp_file_path, max_pred=False)
                    
                    if len(species_predictions) > 0:
                        # Convert predictions to numpy array if not already
                        species_predictions = np.array(species_predictions)
                        # Convert timestamps to numpy array if not already
                        detection_timestamps = np.array(detection_timestamps)
                        
                        # Adjust timestamps to be relative to original file
                        detection_timestamps = detection_timestamps + start_time
                        
                        # Calibrate prediction based on calibration parameters
                        for detection_index in range(len(species_predictions)):
                            species_predictions[detection_index, :] = functions.calibrate(
                                species_predictions[detection_index, :], 
                                calibration_parameters
                            )
                        
                        # Filter predictions with a threshold 
                        species_predictions, species_class_indices, detection_timestamps = functions.threshold_filter(
                            species_predictions, 
                            detection_timestamps, 
                            THRESHOLD
                        )
                        
                        # Adjust prediction based on time of the year and latitude
                        # Todo: Why this is after thresholding? Shouldn't it be before?
                        if INCLUDE_SDM and len(species_predictions) > 0:
                            species_predictions = functions.adjust(
                                species_predictions, 
                                species_class_indices, 
                                migration_parameters, 
                                lat, 
                                lon, 
                                day_of_year
                            )
                        
                        # Loop through predictions
                        for detection_index in range(len(species_predictions)):
                            # Exclude classes 0 and 1, which are humans and noise
                            if species_class_indices[detection_index] <= 1 and not INCLUDE_NOISE:
                                continue
                            
                            # Append results to output file
                            with open(output_file_path, "a") as output_file_writer:
                                output_file_writer.write(
                                    f"{detection_timestamps[detection_index]},"
                                    f"{detection_timestamps[detection_index] + CLIP_DURATION},"
                                    f"{species_name_list['luomus_name'].iloc[species_class_indices[detection_index]]},"
                                    f"{species_name_list['common_name'].iloc[species_class_indices[detection_index]]},"
                                    f"{round(float(species_predictions[detection_index]), 4)}\n"
                                )
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
        "day_of_year": day_of_year,
        "read_day_of_year_from_file": read_day_of_year_from_file,
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
