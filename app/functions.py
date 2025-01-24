import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import rasterio
import os
import yaml
from typing import Optional, Dict, Tuple
import re
from datetime import datetime


def get_data_directory(directory: str) -> Optional[Dict]:
    """
    Checks where audio and data file directory is located, and returns the full path to it.

    Args:
        directory (str): The name of the main directory to search within the "../input/" path.

    Returns:
        path (str): The path to the directory that contains audio and data files, or `None` if the directory is not found.
        error_message (str): Error message if the directory is not found, or `None` if no errors.
    """
    # Check if main directory exists
    directory = f"../input/{directory}"
    if not os.path.isdir(directory):
        print(f"Directory {directory} doesn't exist")
        return None, f"Directory {directory} doesn't exist"
    
    # Check for data subdirectory (case variations)
    for data_dir in ['data', 'Data']:
        potential_path = os.path.join(directory, data_dir)
        if os.path.isdir(potential_path):
            return potential_path, None
    
    # If no data subdirectory found, return main directory
    return directory, None


def get_day_of_year_from_filename(file_name: str) -> Optional[int]:
    """
    Extracts the day of the year from a filename. Supported formats:
    - Audiomoth: 20240527_200000.[extension]
    - Wildlife Acoustics SM4: [prefix]_20240406_015900.[extension]

    Args:
        file_name (str): The name of the file containing the date information.

    Returns:
        Optional[int]: The day of the year as an integer if successfully extracted (1-365 or 1-366 for leap years), or `None` if the date information is not found or invalid.
    """
    # Regular expression to match the date and time format
    pattern = r"(?:.*_)?(\d{8}_\d{6})\.\w+$"
    match = re.search(pattern, file_name)
    
    if match:
        date_str = match.group(1)
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            return date_obj.timetuple().tm_yday
        except ValueError:
            return None
    return None


def get_date_and_time_from_filepath(file_path: str) -> Optional[Tuple[str, str]]:
    """
    Extracts the date and time from a filename. Supported formats:
    - Audiomoth: ../somedirectory/20240527_200000.[extension]
    - Wildlife Acoustics SM4: ../somedirectory/[prefix]_20240406_015900.[extension]

    Args:
        file_path (str): The path to the file containing the date and time information.

    Returns:
        Optional[Tuple[str, str]]: A tuple with date as "YYYYMMDD" and time as "HHMM" if successfully extracted, or `None` if not found or invalid.
    """
    # Get filename from path
    file_name = os.path.basename(file_path)

    # Regular expression to match date (YYYYMMDD) and time (HHMMSS)
    pattern = r"(?:.*_)?(\d{8})_(\d{6})\.\w+(?:\..*)?$"
    match = re.search(pattern, file_name)

    if match:
        date_part = match.group(1)  # Extract YYYYMMDD
        time_part_full = match.group(2)  # Extract HHMMSS

        # Take only the first 4 digits (HHMM) from the time part
        time_part = time_part_full[:4]

        try:
            # Validate date and time format
            datetime.strptime(date_part, "%Y%m%d")  # Validate YYYYMMDD
            datetime.strptime(time_part, "%H%M")    # Validate HHMM
            return date_part, time_part
        except ValueError:
            print(f"Error: Invalid date or time format in file {file_name}")
            return None
    print(f"Error: Date and time not found in file {file_name}")
    return None



# calibrate prediction
def calibrate(species_predictions, calibration_parameters):
    """
    Calibrates prediction probabilities a logistic (sigmoid) transformation to adjust the prediction probabilities for each species based on calibration parameters.

    Args:
        probabilities (list or np.ndarray): List or array of raw prediction probabilities for each species.
        calibration_parameters (np.ndarray): Calibration table, where each row contains logistic regression coefficients (intercept and slope) for each species.

    Returns:
        list: List of calibrated probabilities for each species.
    """
    return [1/(1+np.exp(-(calibration_parameters[i, 0]+calibration_parameters[i, 1]*pr))) for i, pr in enumerate(species_predictions)]


def adjust(species_predictions, species_class_indices, migration_parameters, lat, lon, day_of_year):
    """
    Adjusts species prediction probabilities based on seasonality and geographic occurrence.

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


# Filter and sort predictions based on threshold
# Not used?
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


def threshold_filter(species_predictions, detection_timestamps, threshold = 0.5):
    """
    Filters predictions based on a probability threshold.

    Args:
        prediction_probabilities (np.ndarray): Array of prediction probabilities.
        detection_timestamps (np.ndarray): Array of timestamps corresponding to each prediction.
        probability_threshold (float, optional): Minimum probability required for a prediction to be retained. Defaults to 0.5.

    Returns:
        tuple: Contains three elements:
            - filtered_predictions (np.ndarray): Filtered array of prediction probabilities that exceed the threshold.
            - class_indices (np.ndarray): Array of class indices corresponding to the filtered predictions.
            - filtered_timestamps (np.ndarray): Array of timestamps corresponding to the filtered predictions.
    """

    threshold_indices = np.where(species_predictions>threshold)
    filtered_predictions = species_predictions[threshold_indices]
    class_indices = threshold_indices[1]
    filtered_timestamps = detection_timestamps[threshold_indices[0]]

    return filtered_predictions, class_indices, filtered_timestamps


# pad too short signal with zeros
def pad(signal, x1, x2, target_len=3*48000, sr=48000):
    # signal: input audio signal, x1: starting point in seconds x2: ending point in seconds, 
    # target_len: target length for signal, sr: sampling rate
    sig_out = np.zeros(target_len) 
    sig_out[int(x1*sr):int(x2*sr)] = signal[int(x1*sr):int(x2*sr)]
    return sig_out


# split input signal to overlapping chunks
def split_signal(input_signal, sample_rate, chunk_duration_s, overlap_duration_s):
    """
    Splits an audio signal into multiple overlapping segments, padding shorter segments if necessary to match the desired chunk duration.

    Args:
        input_signal (np.ndarray): The input audio signal to split.
        sample_rate (int): Sampling rate of the input audio signal.
        chunk_duration (float): Target duration of each chunk in seconds.
        overlap_duration (float): Overlap duration between consecutive chunks in seconds.

    Returns:
        list: A list of numpy arrays, where each array is a chunk of the original signal.
    """
    signal_chunks = []
    for i in range(0, len(input_signal), int((chunk_duration_s - overlap_duration_s) * sample_rate)):
        chunk = input_signal[i:i + int(chunk_duration_s * sample_rate)]

        if len(chunk) < int(chunk_duration_s * sample_rate): # Pad if clip is too short
            chunk = pad(chunk, 0, len(chunk)/sample_rate, target_len=int(chunk_duration_s*sample_rate), sr=sample_rate)     
        signal_chunks.append(chunk)

    return signal_chunks


# visualize results of network training
# Not used?
'''
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
'''


def make_output_file_path(output_path, file_name):
    """
    Generates an output file path using BirdNET file name format.

    Args:
        output_path (str): The directory where the output file will be saved.
        file_name (str): The name of the input audio file.

    Returns:
        str: The full path of the output file.
        boolean: True if the file already exists, False otherwise.
    """
    file_name_wo_extension = os.path.splitext(file_name)[0]
    output_file_path = f"{output_path}/{file_name_wo_extension}.Muuttolinnut.results.csv"

    # Check that the output file does not already exist
    if os.path.exists(output_file_path):
        return output_file_path, True

    return output_file_path, False


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


def read_metadata(folder_path: str) -> Optional[Dict]:
    """
    Read a `metadata.yaml` file from a specified folder and return its contents. If the file is not found, cannot be opened, or contains invalid YAML, the function returns `False`.

    Args:
        folder_path (str): The path to the folder containing the `metadata.yaml` file.

    Returns:
        Optional[Dict]: The contents of the `metadata.yaml` file as a dictionary if successfully read and parsed, or `None` if the file does not exist, cannot be read, or contains invalid YAML.
    """
    file_path = os.path.join(folder_path, 'metadata.yaml')
    
    try:
        with open(file_path, 'r') as file:
            metadata = yaml.safe_load(file)

            # Check that contains both lat and lon, with proper decimal values
            if "lat" not in metadata or "lon" not in metadata:
                return None
            if not isinstance(metadata["lat"], (int, float)) or not isinstance(metadata["lon"], (int, float)):
                return None
            # lat should be between -90 and 90, lon between -180 and 180
            if metadata["lat"] < -90 or metadata["lat"] > 90 or metadata["lon"] < -180 or metadata["lon"] > 180:
                return None

            # if day_of_year not set, warn and use 100 as default
            if "day_of_year" not in metadata:
                day_of_year = 100
                print(f"Warning: day_of_year not set in metadata, using default value {day_of_year}")
                metadata["day_of_year"] = day_of_year

            return metadata
    except (FileNotFoundError, yaml.YAMLError, IOError):    
        return None
