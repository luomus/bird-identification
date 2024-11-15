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
clsf = Classifier(path_to_model='../models/model_v3_5.keras', sr=48000, clip_dur=3.0, TFLITE_THREADS = 1, offset=0, dur=0)

# Load species name list and post-processing tables for prediction calibration
species_list = pd.read_csv("classes.csv")
migration_parameters = np.load('Pred_adjustment/migration_params.npy')
calibration_parameters = np.load('Pred_adjustment/calibration_params.npy')

# Get list of files in input folder
# Todo: ignore unsupported file types
files = os.listdir(input_path)

# Create output file with header
#with open(input_path + '_results.txt', 'a') as f:
#    f.write("site, file, species, prediction, detection_time \n")

n_files = len(files)

# Loop each audio file in input folder
for file_index, file in enumerate(files):
    try:
        print(f"Analyzing {file} ({file_index+1}/{n_files})")

        # Predict species
        predictions, detection_times = clsf.classify(input_path + '/' + file, max_pred=False) #max_pred: only keep highest confidence detection for each species instead of saving all detections

        # Calibrate prediction based on calibration parameters
        for prediction_index in range(len(predictions)):
            predictions[prediction_index, :] = calibrate(predictions[prediction_index, :], cal_table=calibration_parameters)
        
        # Ignore human and noise predictions by setting them to zero
        # Todo: remove?
        predictions[:,0:2] = 0

        # Filter predictions with a threshold 
        predictions, c, detection_times = threshold_filter(predictions, detection_times, threshold)

        # Adjust prediction based on time of the year and latitude (only if record is from Finland and location and date are known)
        predictions = adjust(predictions, c, migration_parameters, lat, lon, day_of_year) 

        # Loop through predictions
        for prediction_index in range(len(predictions)):
            if c[prediction_index] > 1: # ignore two first classes: noise and human

                # Save results to output file
                output_filename = f"{output_path}/results.txt"
                with open(output_filename, 'a') as output_file:
                    output_file.write(
                        f"{input_path}, "
                        f"{file}, "
                        f"{species_list['luomus_name'].iloc[c[prediction_index]]}, "
                        f"{predictions[prediction_index]}, "
                        f"{detection_times[prediction_index]}\n"
                    )

        # Clear memory
        gc.collect()

    # Handle exceptions
    except: 
        print(f"Error analyzing {file}!")
        print("Exception type:", type(e).__name__)
        print("Exception message:", str(e))
        print("Traceback:")
        traceback.print_exc()

print("All files analyzed")
print(f"Results saved to {output_filename}")