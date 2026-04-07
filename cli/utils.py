import os
from typing import Optional, Dict, Tuple
import re
from datetime import datetime


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
    The check is case-insensitive.

    Args:
        input_path (str): The directory where the audio files are.

    Returns:
        list: A list of audio file names.
    """
    supported_extensions = [".wav", ".mp3", ".flac"]
    files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and f.lower().endswith(tuple(supported_extensions))]
    return files


def read_metadata(folder_path: str) -> Optional[Dict]:
    """
    Read a `metadata.yaml` file from a specified folder and return its contents. If the file is not found, cannot be opened, or contains invalid YAML, the function returns `False`.

    Args:
        folder_path (str): The path to the folder containing the `metadata.yaml` file.

    Returns:
        Optional[Dict]: The contents of the `metadata.yaml` file as a dictionary if successfully read and parsed, or `None` if the file does not exist, cannot be read, or contains invalid YAML.
    """
    import yaml

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
