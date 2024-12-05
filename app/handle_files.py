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

import functions
import stats_functions


def get_datafile_list(directory: str) -> Optional[list]:
    """
    Reads and returns a list of data files in the directory.

    Args:
        directory (str): The name of the directory containing the data files.

    Returns:
        Optional[list]: List of data files in the directory, or `None` if no files are found.
    """

    # Check if directory exists
    if not os.path.isdir(directory):
        print(f"Data directory {directory} doesn't exist")
        return None

    # Get list of files with ".csv" extentions in directory
    data_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    # Append directory to filenames
    data_files = [os.path.join(directory, f) for f in data_files]

    if len(data_files) == 0:
        print(f"Data directory {directory} doesn't contain any data files")
        return None
    
    return data_files


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

            # Add a new column with the filename
            # Split file path by "/" and take the last part
            file_name = os.path.basename(file_path)
            df['Filename'] = file_name.replace('.csv', '')

            df = df[df['Confidence'] >= threshold]

            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    combined_dataframe = pd.concat(dataframes, ignore_index=True)
    return combined_dataframe
    

def handle_files(main_directory, threshold):

    datafile_directory = functions.get_data_directory(main_directory)
    print("Getting data from ", datafile_directory)

    data_files = get_datafile_list(datafile_directory)
    print(f"Loaded { len(data_files) } data files")

    output_directory = make_output_directory(main_directory)
    print("Created directory ", output_directory) 

    df = load_csv_files_to_dataframe(data_files, threshold)

#    print(df)
    print(f"Loaded { len(df) } rows of data")

    # Generate statistics
    species_counts = df['Scientific name'].value_counts()
    print(species_counts)

#    stats_functions.generate_historgrams(df, threshold, output_directory)

    # Randomly sample 5 rows per 'Scientific name' group
    random_samples = (
        df.groupby('Scientific name')
        .apply(lambda group: group.sample(n=5, replace=False) if len(group) >= 5 else group)
        .reset_index(drop=True)
    )
    print(random_samples)


handle_files("test", 0.7)
