#!/usr/bin/env python3

import argparse
import sys
import os
import run_model


def get_data_directory(directory: str) -> str:
    # Check if main directory exists
    directory = f"../input/{directory}"
    if not os.path.isdir(directory):
        return False
    
    # Check for data subdirectory (case variations)
    for data_dir in ['data', 'Data']:
        potential_path = os.path.join(directory, data_dir)
        if os.path.isdir(potential_path):
            return potential_path
    
    # If no data subdirectory found, return original directory
    return directory


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Analyze bird audio recordings from a specific location.'
    )
    
    # Add required arguments
    parser.add_argument(
        '--dir',
        type=str,
        required=True,
        help='Directory that contains the audio files'
    )

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # Handle --help or invalid arguments
        return

    # Validate

    # Check if directory exists
    data_directory = get_data_directory(args.dir)
    if not data_directory:
        print(f"Error: Directory '{args.dir}' not found", file=sys.stderr)
        return

    parameters = {
        "lat": 60,
        "lon": 25,
        "day_of_year": 200,
        "apply_sdm_adjustments": True,
        "ignore_nonbirds": True,
        "threshold": 0.3
    }

    try:
        # Call the analyze_directory function with provided coordinates
        success = run_model.analyze_directory(data_directory, parameters)
    except Exception as e:
        print(f"Error during analysis: {str(e)}", file=sys.stderr)
        # Print full traceback
        raise
        sys.exit(1)

if __name__ == "__main__":
    main()