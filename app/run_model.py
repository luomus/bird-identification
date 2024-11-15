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

# load classification model
# TFLITE_THREADS can be as high as number of CPUs available, the rest of the parameters should not be changed
clsf = Classifier(path_to_model='../models/model_v3_5.keras', sr=48000, clip_dur=3.0, TFLITE_THREADS = 1, offset=0, dur=0) 

# load species list and post-processing tables for prediction calibration
sp_list=pd.read_csv("classes.csv")
migr_table = np.load('Pred_adjustment/migration_params.npy')
cal_table = np.load('Pred_adjustment/calibration_params.npy')

# analyze all files
files = os.listdir(input_path)

with open(input_path + '_results.txt', 'a') as f:
    f.write("site, file, species, prediction, detection_time \n")

n_files = len(files)
for j, fi in enumerate(files):
    try:
        print(f"Analyzing {fi} ({j+1}/{n_files})...")
        # predict for example clip
        pred, t = clsf.classify(input_path + '/' + fi, max_pred=False) #max_pred: only keep highest confidence detection for each species instead of saving all detections
        # calibrate prediction 
        for i in range(len(pred)):
            pred[i, :] = calibrate(pred[i, :], cal_table=cal_table)
        # ignore human and noise predictions
        pred[:,0:2] = 0 
        # filter predictions with a threshold 
        pred, c, t = threshold_filter(pred, t, threshold)
        # adjust prediction based on time of the year and latitude (only if record is from Finland and location and date are known)
        pred = adjust(pred, c, migr_table, lat, lon, day_of_year) 
        # filter and find species names from sp_list
        for i in range(len(pred)):
            if c[i] > 1: # ignore two first classes: noise and human
                output_filename = f"{output_path}/results.txt"
                with open(output_filename, 'a') as f:
                    f.write(input_path + ", " + fi + ", " + str(sp_list['common_name'].iloc[c[i]]) + ", " + str(pred[i]) + ", " + str(t[i]) + "\n")
        gc.collect() # clear memory
    except: 
        print(f"Error analyzing {fi}!")
        print("Exception type:", type(e).__name__)
        print("Exception message:", str(e))
        print("Traceback:")
        traceback.print_exc()

print(" ")
print("All files analyzed")
print(f"Results saved to {output_filename}")