import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import rasterio
import os

# calibrate prediction
def calibrate(p, cal_table):
    return [1/(1+np.exp(-(cal_table[i, 0]+cal_table[i, 1]*pr))) for i, pr in enumerate(p)]


def adjust(species_predictions, species_class_indices, migration_parameters, lat, lon, day_of_year):
    """Adjusts species prediction probabilities based on migration patterns and geographic occurrence.

    This function refines species presence probabilities from the model, adjusting for 
    migration timing and spatial occurrence within a geographic area (latitude and longitude).
    Adjustments account for seasonality, geographic distributions, and potential map overlays.

    Args:
        species_predictions (np.ndarray): Array of prediction probabilities for each species.
        species_class_indices (np.ndarray): Array of class indices for each species.
        migration_parameters (np.ndarray): Migration parameters table, where each row contains migration parameters for a species.
        latitude (float): Latitude coordinate for the recording location.
        longitude (float): Longitude coordinate for the recording location.
        day_of_year (int): Day of the year (1-365/366) representing the time of observation.

    Returns:
        np.ndarray: Array of adjusted prediction probabilities for each species.
    """
    # Handle leap year with 366 days
    if day_of_year > 365:
        day_of_year = 365
    for species_index in range(len(species_predictions)):
        species_class_index = species_class_indices[species_index]   

        # Skipping the first 2 classes (noise and human)
        if species_class_index <= 1:
            continue

        # Probability that species has migrated to Finland
        sp_migration_parameters = migration_parameters[species_class_index, :]
        migration_probability = np.min((norm.cdf(day_of_year, loc=sp_migration_parameters[0]+sp_migration_parameters[1]*lat, scale=sp_migration_parameters[4]/2), 
              1-norm.cdf(day_of_year, loc=sp_migration_parameters[2]+sp_migration_parameters[3]*lat, scale=sp_migration_parameters[5]/2)))
        
        # Probability that species occurs in given area
        with rasterio.open('Pred_adjustment/distribution_maps/'+ str(species_class_index)+ '_a.tif') as src:
            for value in src.sample([(lon, lat)]): 
                geo_presence_probability = value
        geo_presence_probability = geo_presence_probability[0]
        if np.isnan(geo_presence_probability): # if no information from given location, species is considered possible
            geo_presence_probability=1
        
        # Use additional map for given time of the year:
        time_presence_probability = 0
        use_map_b = 0
        if(sp_migration_parameters[6]<sp_migration_parameters[7]):
            if((day_of_year>=sp_migration_parameters[6]) & (day_of_year<=sp_migration_parameters[7])):
                use_map_b = 1
        if(sp_migration_parameters[6]>sp_migration_parameters[7]):
            if((day_of_year>=sp_migration_parameters[6]) or (day_of_year<=sp_migration_parameters[7])):
                use_map_b = 1
        
        if use_map_b==1:
            with rasterio.open('Pred_adjustment/distribution_maps/'+ str(species_class_index)+ '_b.tif') as src:
                for value in src.sample([(lon, lat)]): 
                    time_presence_probability = value
            time_presence_probability = time_presence_probability[0]
            if np.isnan(time_presence_probability):
                time_presence_probability=1

        # Adjustment based on probability of species being present
        presence_probability = migration_probability * (geo_presence_probability + (1-geo_presence_probability)*use_map_b*time_presence_probability)
        adjusted_score = np.minimum(0, np.log10(presence_probability)+1)
        adjusted_score = np.maximum(adjusted_score, -10) # avoid -inf
        species_predictions[species_index] = (np.maximum(0, species_predictions[species_index]+adjusted_score*0.25))/np.maximum(0.0001, (1+adjusted_score*0.25))
        
    return species_predictions


# filter and sort predictions based on threshold
def top_preds(prediction, timestamps, threshold=0.5):
    # prediction: classification model output (max results), timestamp: timestamps from model, threshold: threshold for filtering (0-1)
    cls= [idx for idx, val in enumerate(prediction) if val > threshold]
    prediction = np.array(prediction)[cls]
    ts = np.array(timestamps)[cls]
    if len(cls)>0:
        prediction, cls, ts = map(list, zip(*sorted(zip(prediction, cls, ts), reverse=True)))
    else:
        prediction=[]
        cls = []
        ts = []
    return prediction, cls, ts

# filter predictions based on threshold
def threshold_filter(preds, timestamps, threshold=0.5):
    # prediction: classification model output (all results), timestamp: timestamps from model, threshold: threshold for filtering (0-1)
    arg_where = np.where(preds>threshold)
    prediction = preds[arg_where]
    cls = arg_where[1]
    ts = timestamps[arg_where[0]]
    return prediction, cls, ts

# pad too short signal with zeros
def pad(signal, x1, x2, target_len=3*48000, sr=48000):
    # signal: input audio signal, x1: starting point in seconds x2: ending point in seconds, 
    # target_len: target length for signal, sr: sampling rate
    sig_out = np.zeros(target_len) 
    sig_out[int(x1*sr):int(x2*sr)] = signal[int(x1*sr):int(x2*sr)]
    return sig_out

# split input signal to overlapping chunks
def split_signal(sig, rate, seconds, overlap):
    # sig: input_signal, rate: sampling rate, seconds: target length in seconds,
    # overlap: overlap of consecutive frames in seconds, minlen: m
    sig_splits = []
    for i in range(0, len(sig), int((seconds - overlap) * rate)):
        split = sig[i:i + int(seconds * rate)]
        if len(split) < int(seconds * rate): # pad if clip is too short
            split = pad(split, 0, len(split)/rate, target_len=int(seconds*rate), sr=rate)     
        sig_splits.append(split)
    return sig_splits

# visualize results of network training
def plot_results(history, val = True):
    # history: model history object, val: show validation results
    acc = history['binary_accuracy']
    loss = history['loss']
    if val:
        val_acc = history['val_binary_accuracy']
        val_loss = history['val_loss']
    epochs = range(1, len(acc) + 1)
    plt.plot(epochs, acc, 'bo', label='Training acc')
    if val:
        plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training (and validation) accuracy')
    plt.legend()
    plt.figure()
    plt.plot(epochs, loss, 'bo', label='Training loss')
    if val:
        plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training (and validation) loss')
    plt.legend()
    plt.show()

def make_output_file_path(output_path, file_name):
    """
    Generates an output file path using BirdNET file name format.

    Args:
        output_path (str): The directory where the output file will be saved.
        file_name (str): The name of the input audio file.

    Returns:
        str: The full path of the output file.
    """
    file_name_wo_extension = os.path.splitext(file_name)[0]
    output_file_path = f"{output_path}/{file_name_wo_extension}.Muuttolinnut.results.csv"
    return output_file_path


def get_audio_file_names(input_path):
    """
    Returns a list of audio files in the input folder. Includes only files with specific extensions.

    Args:
        input_path (str): The directory where the audio files are.

    Returns:
        list: A list of audio file names.
    """
    supported_extensions = [".wav", ".mp3", ".flac"]
    files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and f.endswith(tuple(supported_extensions))]
    return files

