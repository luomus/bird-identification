'''
# Script that reads csv files of bird identifications, generates some statistics, and picks set of validation audio data from corresponding audio files.

Overall process:
- User gives a directory name as an argument.
- Validate the input, check that directory exists and contains proper files
- Generate output directory
- Read data from csv files (1-n) into Pandas DataFrame
- Generate statistics from the data
- Save statistics into an Excel file
- Generate histogram for each species and save them into the output directory
- Pick a set of predicted occurrences for validation, aiming for a variety of days and confidence values
- Picks short audio segments from the corresponding audio files, saving them to the output directory
- Generates an HTML report to the output directory with adio files, spectrograms, and predictions
'''

import os   
from typing import Optional, Dict
from datetime import datetime
import pandas as pd

import librosa
import soundfile as sf

import functions
import stats_functions

import time
import tracemalloc


def get_datafile_list(directory: str) -> Optional[list]:
    """
    Reads and returns a list of data files in the directory.

    Args:
        directory (str): The name of the directory containing the data files.

    Returns:
        Optional[list]: List of data files in the directory, or `None` if no files are found.
    """

    audio_extensions = ['wav', 'mp3', 'flac']

    # Check if directory exists
    if not os.path.isdir(directory):
        print(f"Error: data directory {directory} doesn't exist")
        return None

    # Get list of files with ".csv" extentions in directory
    data_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    # Append directory to filenames
    data_files = [os.path.join(directory, f) for f in data_files]

    if len(data_files) == 0:
        print(f"Error: data directory {directory} doesn't contain any data files")
        return None

    return data_files


def check_audio_files(data_file_paths, audio_extensions=('wav', 'mp3', 'flac')):
    """
    Check if corresponding audio files exist for each data file.
    
    Args:
        data_file_paths (list): List of paths to data files.
        audio_extensions (tuple): Possible extensions for audio files.
        
    Returns:
        str or None: The common audio file extension if all corresponding files are found, else None.
    """
    # Dictionary to store the matched audio extension count
    extension_counts = {ext: 0 for ext in audio_extensions}

    # Iterate through each data file
    for file_path in data_file_paths:
        # Extract the directory and filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Extract part1 and part2 from the filename "[part1].[part2].results.csv"
        if not filename.endswith(".results.csv"):
            print("Error: Invalid file format, missing .results.csv extension")
            return None  # Invalid file format
        
        try:
            part1, part2 = filename.split(".results.csv")[0].split(".")
        except ValueError:
            print("Error: Incorrectly formatted file name")
            return None  # Incorrectly formatted file name
        
        # Check for corresponding audio files with valid extensions
        audio_file_found = False
        for ext in audio_extensions:
            audio_file = os.path.join(directory, f"{part1}.{ext}")
            if os.path.isfile(audio_file):
                extension_counts[ext] += 1
                audio_file_found = True
                break

        if not audio_file_found:
            return None  # Missing corresponding audio file for this data file

    # Determine if one extension consistently matches all files
    for ext, count in extension_counts.items():
        if count == len(data_file_paths):
            return ext

    print("Error: Inconsistent audio file extensions")
    return None


def make_output_directory(main_directory: str) -> Optional[str]:
    """
    Creates a new output directory for the report.

    Args:
        main_directory (str): The name of the main directory for the report.
    
    Returns:
        str: The name of the new output directory, or `None` if the directory couldn't be created.
    """

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y%m%d_%H%M%S')
    output_directory = f"../input/{ main_directory }/report_{ formatted_datetime }"

    try:
        os.makedirs(output_directory)
    except OSError:
        print(f"Error: Could not create output directory {output_directory}")
        return None

    return output_directory


def load_csv_files_to_dataframe(file_paths: list[str], threshold: float) -> pd.DataFrame:
    """
    Given a list of CSV file names, loads their contents into a single pandas DataFrame.
    
    Parameters:
    - file_names (list): List of file paths to the CSV files.
    - threshold (float): The threshold value used to filter rows.
    
    Returns:
    - pandas.DataFrame: Combined DataFrame containing all the CSV files' contents.
    """
    dataframes = []

    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)

            # Add new column with the file path
            df['Filepath'] = file_path

            df['Audio Filepath'] = df['Filepath'].apply(get_audio_file_path)

            # Add a new column with the filename
            # Split file path by "/" and take the last part
#            file_name = os.path.basename(file_path)
#            df['Filename'] = file_name.replace('.csv', '')

            # Filter rows by threshold
            df = df[df['Confidence'] >= threshold]

            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    combined_dataframe = pd.concat(dataframes, ignore_index=True)
    return combined_dataframe


def get_audio_file_path(file_path):
    """
    Given a file path, removes the suffix starting from the third dot from the right.
    Checks if a file with extensions '.flac', '.wav', or '.mp3' exists and returns the new path.
    If no such file exists, returns None.
    """
    # Split the file path into directory and file name
    dir_name, file_name = os.path.split(file_path)

    # Split the file name on dots
    parts = file_name.split('.')

    # Ensure there are at least 4 parts for the third dot from the right
    if len(parts) < 4:
        print(f"Error: Incorrectly formatted file name: {file_name}")
        return None  # Not enough parts to remove the suffix properly

    # Reconstruct the file name without the suffix from the third dot from the right
    new_file_name = '.'.join(parts[:-3])  # Keep all parts up to the third dot from the right

    # Possible audio file extensions
    audio_extensions = ['.wav', '.flac', '.mp3']

    # Check for each audio extension
    for ext in audio_extensions:
        new_path = os.path.join(dir_name, new_file_name + ext)
        if os.path.exists(new_path):
            return new_path  # Return the first found audio file path

    # If no file with the given extensions is found
    print(f"Error: No audio file found for {file_path}")
    return None


import pandas as pd

def get_detection_examples(df: pd.DataFrame, example_count: int = 5) -> pd.DataFrame:
    """
    Gets example audio segments; a subset of rows from an audio detection dataframe i.e., specific rows for each unique value in 'Scientific name'.
    - Row with the lowest value in 'Start (s)'
    - Row with the highest value in 'Start (s)'
    - Row with the highest value in 'Confidence'
    - Row with the lowest value in 'Confidence'
    - 0...n random rows
    Parameters:
    - df (pandas.DataFrame): The input DataFrame.
    - example_count (int): The number of examples to take for each unique value in 'Scientific name'.
    Returns:
    - pandas.DataFrame: A subset of the input DataFrame, with data about the selected examples.
    """
    if example_count < 5:
        example_count = 5
    random_count = example_count - 4
    result_rows = []
    unique_names = df["Scientific name"].unique()

    for name in unique_names:
        subset = df[df["Scientific name"] == name]
        selected_indices = set()  # To keep track of selected rows
        
        # Row with lowest 'Start (s)' value
        row_lowest_start = subset.loc[subset["Start (s)"].idxmin()]
        selected_indices.add(row_lowest_start.name)
        result_rows.append(row_lowest_start.to_dict() | {"Type": "first"})
        
        # Row with highest 'Start (s)' value
        remaining = subset.drop(index=list(selected_indices))
        if not remaining.empty:
            row_highest_start = remaining.loc[remaining["Start (s)"].idxmax()]
            selected_indices.add(row_highest_start.name)
            result_rows.append(row_highest_start.to_dict() | {"Type": "last"})
        
        # Row with highest 'Confidence' value
        remaining = subset.drop(index=list(selected_indices))
        if not remaining.empty:
            row_highest_confidence = remaining.loc[remaining["Confidence"].idxmax()]
            selected_indices.add(row_highest_confidence.name)
            result_rows.append(row_highest_confidence.to_dict() | {"Type": "highest confidence"})
        
        # Row with lowest 'Confidence' value
        remaining = subset.drop(index=list(selected_indices))
        if not remaining.empty:
            row_lowest_confidence = remaining.loc[remaining["Confidence"].idxmin()]
            selected_indices.add(row_lowest_confidence.name)
            result_rows.append(row_lowest_confidence.to_dict() | {"Type": "lowest confidence"})
        
        # Random rows
        remaining = subset.drop(index=list(selected_indices))
        if not remaining.empty:
            random_rows = remaining.sample(n=min(len(remaining), random_count))
            for _, row in random_rows.iterrows():
                result_rows.append(row.to_dict() | {"Type": "random"})
                selected_indices.add(row.name)
    
    # Combine all rows into a new DataFrame
    result_df = pd.DataFrame(result_rows).drop_duplicates()
    return result_df


def make_soundfiles(example_species_predictions_df, output_directory, PADDING_SECONDS):
    """
    Given a DataFrame of example species predictions, extracts audio segments from the corresponding audio files and saves them to the output directory.

    DataFrame is in this format:
    Start (s)  End (s)    Scientific name         Common name  Confidence                                                          Filepath                                Audio Filepath
    0          0.0      3.0  Luscinia luscinia  Thrush Nightingale       0.944  ../input/suomenoja/Data/20240517_000000.Muuttolinnut.results.csv  ../input/suomenoja/Data/20240517_000000.flac
    1       3594.0   3597.0  Luscinia luscinia  Thrush Nightingale       0.616  ../input/suomenoja/Data/20240516_220000.Muuttolinnut.results.csv  ../input/suomenoja/Data/20240516_220000.flac
    2       2754.0   2757.0  Luscinia luscinia  Thrush Nightingale       0.300  ../input/suomenoja/Data/20240516_230000.Muuttolinnut.results.csv  ../input/suomenoja/Data/20240516_230000.flac
    3        908.0    911.0  Luscinia luscinia  Thrush Nightingale       0.960  ../input/suomenoja/Data/20240517_000000.Muuttolinnut.results.csv  ../input/suomenoja/Data/20240517_000000.flac
    4       2074.0   2077.0  Luscinia luscinia  Thrush Nightingale       0.610  ../input/suomenoja/Data/20240517_230000.Muuttolinnut.results.csv  ../input/suomenoja/Data/20240517_230000.flac

    """

    # Loop though example_species_predictions_df, i.e. species predictions
    for index, row in example_species_predictions_df.iterrows():

        segment_start = row['Start (s)'] - PADDING_SECONDS
        segment_end = row['End (s)'] + PADDING_SECONDS

        if segment_start < 0:
            segment_start = 0
        
        # TODO: speed this up slightly by caching file durations to a global variable
        audio_duration = librosa.get_duration(path = row['Audio Filepath'])

        if segment_end > audio_duration:
            segment_end = audio_duration

        # Generate segment filename
        file_name_with_ext = os.path.basename(row["Audio Filepath"])
        base_file_name, extension = os.path.splitext(file_name_with_ext)

        segment_filepath = f"{ output_directory }/{ base_file_name }_{ row['Scientific name'].replace(' ', '-') }_{ int(segment_start) }_{ int(segment_end) }_{ round(row['Confidence'], 3) }{ extension }"

        # Load only the segment into memory
        y, sr = librosa.load(row["Audio Filepath"], offset= segment_start, duration = (segment_end - segment_start))

        # Save the segment to a new file
        sf.write(segment_filepath, y, sr, format='FLAC')

        print("Segment saved to ", segment_filepath)

        # Add segment filename to dataframe
        example_species_predictions_df.loc[index, 'Segment Filepath'] = segment_filepath

    return example_species_predictions_df


def seconds_to_time(seconds):
    """
    Convert seconds into minutes and seconds format.
    
    Args:
        seconds (float): Number of seconds to convert
        
    Returns:
        str: Formatted string in "M min, S s" format
    """

    seconds = int(seconds)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} min, {remaining_seconds} s"


def generate_html_report(example_species_predictions_df, species_counts, output_directory):
    """
    Generates a HTML report for the example species predictions. Each example is displayed as a card with these information:
    - Scientific name
    - Common name
    - Confidence
    - Audio player for the segment

    The cards are grouped under Scientific name headings.

    Parameters:
    - example_species_predictions_df (pandas.DataFrame): DataFrame containing the example species predictions.
    - species_counts (dict): Dictionary containing the counts of each species in the DataFrame.
    - output_directory (str): The directory to save the audio segments.

    Returns:
    - output_file_path (str): The path to the saved audio segment, or None if the report couldn't be generated.
    """

    # Create a new HTML file
    html_file_path = f"{ output_directory }/_report.html"

    with open(html_file_path, 'w') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write(f"<title>Report { output_directory }</title>\n")
        f.write("""
        <style>
            body {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            div {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 10px;
                padding: 10px;
            }
            h2 {

            }
            p {

            }
        </style>
        """)
        f.write("</head>\n")
        f.write("<body>\n")
        f.write(f"<h1>Report { output_directory }</h1>\n")
        f.write(f"<p>Generated at { datetime.now() }</p>\n")

        scientific_name_mem = ""
        for index, row in example_species_predictions_df.iterrows():

            if row['Scientific name'] != scientific_name_mem:
                if scientific_name_mem != "":
                    f.write("</div>\n")
                scientific_name_mem = row['Scientific name']

                count = species_counts.get(row['Scientific name'], 0)
                histogram_file = f"{ row['Scientific name'].replace(' ', '_') }.png"

                f.write(f"<h2><span class='common'>{ row['Common name'] }</span> <em class='sci'>({ row['Scientific name'] })</em>, <span class='count'>{ count }</span> detections</h2>\n")
                f.write(f"<img src='{ histogram_file }' alt='Histogram for { row['Scientific name'] }'>\n")

                f.write("<div class='species'>\n")

            filename = os.path.basename(row['Segment Filepath'])
            parts = filename.split('.')
            extension = parts[-1]

            f.write(f"<div class='example'>\n")
            f.write(f"<h3><span class='type'>{ row['Type'] }</span>, <span class='confidence'>{ round(row['Confidence'], 3) }</span></h3>\n")
            f.write(f"<audio controls><source src='{ filename }' type='audio/{ extension }'></audio>\n")
            f.write(f"<p><span class='filename'>{ filename }</span>, <span class='timestamp'>{ seconds_to_time(row['Start (s)']) }</span></p>\n")
            f.write(f"</div>\n")

        f.write("</div>\n")
        f.write("</body>\n")
        f.write("</html>\n")

    print("HTML report saved to ", html_file_path)
    return html_file_path



def handle_files(main_directory, threshold):

    # Start benchmarking
    tracemalloc.start()
    start_time = time.perf_counter()

    # Settings for development
    pd.set_option('display.max_colwidth', None) # Prevent truncating cell content
    pd.set_option('display.width', 0)           # Adjust width for large data

    PADDING_SECONDS = 1
    EXAMPLE_COUNT = 4

    # Check input data is ok
    datafile_directory = functions.get_data_directory(main_directory)
    print("Getting data from ", datafile_directory)

    data_files = get_datafile_list(datafile_directory)
    print(f"Loaded { len(data_files) } data files")
#    print(data_files)

#    audio_extension = check_audio_files(data_files)
#    print(f"Audio extension: {audio_extension}")

    # Load and analyze data
    species_predictions_df = load_csv_files_to_dataframe(data_files, threshold)

    print(f"Loaded { len(species_predictions_df) } rows of data")

    # Generate statistics
    species_counts = species_predictions_df['Scientific name'].value_counts()
    print(species_counts)

    # Prepare report
    output_directory = make_output_directory(main_directory)
    print("Created directory ", output_directory)

    stats_functions.generate_historgrams(species_predictions_df, threshold, output_directory)

    # Pick examples for validation
    example_species_predictions_df = get_detection_examples(species_predictions_df, EXAMPLE_COUNT)
#    print(example_species_predictions_df)

    # Loop through the example rows and extract audio segments
    example_species_predictions_df = make_soundfiles(example_species_predictions_df, output_directory, PADDING_SECONDS)

#    print(example_species_predictions_df)

    # Generate HTML report
    report_filepath = generate_html_report(example_species_predictions_df, species_counts, output_directory)

    # End benchmarking
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.4f} seconds")

    current, peak = tracemalloc.get_traced_memory()

    print(f"Current memory usage: {current / (1024 * 1024):.2f} MB")
    print(f"Peak memory usage: {peak / (1024 * 1024):.2f} MB")

    # Stop tracing
    tracemalloc.stop()


handle_files("test", 0.8)
