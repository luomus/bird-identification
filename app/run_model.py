import pandas as pd
import numpy as np
import os
import gc
import tensorflow as tf
from tensorflow import keras
from classifier import Classifier
from functions import calibrate, adjust, threshold_filter
import traceback

# ---------------------------------------------------------------------------
# User-defined parameters

threshold = 0.3 # only save predictions with confidence higher than threshold

# Rocksberg test data
lat = 60.19
lon = 24.62
day_of_year = 126

# ---------------------------------------------------------------------------

# Settings

input_path = "../input" # Input folder for audio files
output_path = "../output" # Output folder for results

# Load classification model
# TFLITE_THREADS can be as high as number of CPUs available, the rest of the parameters should not be changed
audio_classifier = Classifier(path_to_model='../models/model_v3_5.keras', sr=48000, clip_dur=3.0, TFLITE_THREADS = 1, offset=0, dur=0)

# Load species name list and post-processing tables for prediction calibration
species_name_list = pd.read_csv("classes.csv")
migration_parameters = np.load('Pred_adjustment/migration_params.npy')
calibration_parameters = np.load('Pred_adjustment/calibration_params.npy')

# Get list of files in input folder
# Todo: ignore unsupported file types
files = os.listdir(input_path)



n_files = len(files)

# Loop each audio file in input folder
for file_index, file_name in enumerate(files):
    try:
        file_path = input_path + '/' + file_name
        print(f"Analyzing {file_path} ({file_index + 1} of {n_files})")

        # Output filename with BirdNET format
        file_name_wo_extension = os.path.splitext(file_name)[0]
        output_file_path = f"{output_path}/{file_name_wo_extension}.Muuttolinnut.results.csv"

        # Create output file with header
        with open(output_file_path, 'a') as output_file_writer:
            output_file_writer.write("site, filename, species, prediction, detection_time \n")

        # Predict species
        species_predictions, detection_timestamps = audio_classifier.classify(file_path, max_pred=False) #max_pred: only keep highest confidence detection for each species instead of saving all detections

        # Calibrate prediction based on calibration parameters
        for detection_index in range(len(species_predictions)):
            species_predictions[detection_index, :] = calibrate(species_predictions[detection_index, :], cal_table=calibration_parameters)
        
        # Ignore human and noise predictions by setting them to zero
        # Todo: remove?
        species_predictions[:,0:2] = 0

        # Filter predictions with a threshold 
        species_predictions, species_class_indices, detection_timestamps = threshold_filter(species_predictions, detection_timestamps, threshold)

        # Adjust prediction based on time of the year and latitude (only if record is from Finland and location and date are known)
        species_predictions = adjust(species_predictions, species_class_indices, migration_parameters, lat, lon, day_of_year) 

        # Loop through predictions
        for detection_index in range(len(species_predictions)):
            if species_class_indices[detection_index] > 1: # ignore two first classes: noise and human

                # Save results to output file
#                output_filename = f"{output_path}/results.txt"
                with open(output_file_path, 'a') as output_file_writer:
                    output_file_writer.write(
                        f"{input_path}, "
                        f"{file_name}, "
                        f"{species_name_list['luomus_name'].iloc[species_class_indices[detection_index]]}, "
                        f"{species_predictions[detection_index]}, "
                        f"{detection_timestamps[detection_index]}\n"
                    )

        # Clear memory
        gc.collect()

    # Handle exceptions
    except: 
        print(f"Error analyzing {file_name}!")
        print("Exception type:", type(e).__name__)
        print("Exception message:", str(e))
        print("Traceback:")
        traceback.print_exc()

print("All files analyzed")
#print(f"Results saved to {output_filename}")