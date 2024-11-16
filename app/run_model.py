import pandas as pd
import numpy as np
import os
import gc
from tensorflow import keras
from classifier import Classifier
import functions
import traceback

import librosa
import soundfile as sf
import tempfile

# ---------------------------------------------------------------------------
# User-defined parameters

threshold = 0.3 # only save predictions with confidence higher than threshold
tflite_threads = 2
ignore_nonbirds = True # whether to ignore human and noise predictions
do_sdm_adjustments = True # Whether to adjust confidence values based on the species distribution and temporal model

# Espoo test data
lat = 60.19 
lon = 24.62
day_of_year = 126 # 6th of May
#day_of_year = 156 # 5th of June

# ---------------------------------------------------------------------------

# Settings

input_path = "../input" # Input folder for audio files
output_path = "../output" # Output folder for results
path_to_model = "../models/model_v3_5.keras"

# Load classification model
# TFLITE_THREADS can be as high as number of CPUs available, the rest of the parameters should not be changed
CLIP_DURATION = 3.0
audio_classifier = Classifier(path_to_model=path_to_model, sr=48000, clip_dur=CLIP_DURATION, TFLITE_THREADS=tflite_threads, offset=0, dur=0)

# Load species name list and post-processing tables for prediction calibration
species_name_list = pd.read_csv("classes.csv")
migration_parameters = np.load("Pred_adjustment/migration_params.npy")
calibration_parameters = np.load("Pred_adjustment/calibration_params.npy")

# Get list of files in input folder
files = functions.get_audio_file_names(input_path)

number_of_files = len(files)

# Define segment length (10 minutes in seconds)
SEGMENT_LENGTH = 600

# Loop each audio file in input folder
for file_index, file_name in enumerate(files):
    try:
        file_path = f"{input_path}/{file_name}"
        output_file_path = functions.make_output_file_path(output_path, file_name)
        print(f"Analyzing {file_path} ({file_index + 1} of {number_of_files})")

        # Create an empty output file with header
        with open(output_file_path, "w") as output_file_writer:
            output_file_writer.write("Start (s),End (s),Scientific name,Common name,Confidence\n")

        # Load audio file
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=audio_data, sr=sample_rate)
        
        # Create temporary directory for segments
        with tempfile.TemporaryDirectory() as temp_dir:
            # Split into segments
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
                            cal_table=calibration_parameters
                        )
                    
                    # Filter predictions with a threshold 
                    species_predictions, species_class_indices, detection_timestamps = functions.threshold_filter(
                        species_predictions, 
                        detection_timestamps, 
                        threshold
                    )
                    
                    # Adjust prediction based on time of the year and latitude
                    if do_sdm_adjustments and len(species_predictions) > 0:
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
                        if ignore_nonbirds and species_class_indices[detection_index] <= 1:
                            continue
                        
                        # Append results to output file
                        with open(output_file_path, "a") as output_file_writer:
                            output_file_writer.write(
                                f"{detection_timestamps[detection_index]},"
                                f"{detection_timestamps[detection_index] + CLIP_DURATION},"
                                f"{species_name_list['luomus_name'].iloc[species_class_indices[detection_index]]},"
                                f"{species_name_list['common_name'].iloc[species_class_indices[detection_index]]},"
                                f"{species_predictions[detection_index]}\n"
                            )
                
            # Clear memory after processing each file
            gc.collect()

    # Handle exceptions
    except Exception as e: 
        print(f"Error analyzing {file_name}!")
        print(f"Error details: {str(e)}")
        raise  # This will show the full traceback

print("All files analyzed")
#print(f"Results saved to {output_filename}")