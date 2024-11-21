#!/usr/bin/env python3

import argparse
import sys
import os
import run_model
from typing import Optional, Dict


def get_data_directory(directory: str) -> Optional[Dict]:
    """
    Retrieve the path to the data directory, if it exists.

    Args:
        directory (str): The name of the main directory to search within the "../input/" path.

    Returns:
        Optional[Dict]: The path to the directory that contains audio files, or `None` if the directory is not found.
    """
    # Check if main directory exists
    directory = f"../input/{directory}"
    if not os.path.isdir(directory):
        return None
    
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
    parser.add_argument(
        '--thr',
        type=float,
        default=0.5,
        help='Threshold for species prediction filtering.'
    )
    parser.add_argument(
        '--noise',
        action='store_true',
        help='Ignore non-bird species predictions.'
    )
    parser.add_argument(
        '--sdm',
        action='store_true',
        help='Enable species distribution model adjustments.'
    )
    parser.add_argument(
        '--skip',
        action='store_true',
        help='Whether to skip analyzing a file if output file already exists.'
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
    if data_directory is None:
        print(f"Error: Directory '{args.dir}' not found", file=sys.stderr)
        return

    # Check if threshold is within valid range
    if args.thr < 0 or args.thr > 1:
        print("Error: Threshold must be between 0 and 1", file=sys.stderr)
        return
    
    # Set parameters
    parameters = {
        'threshold': args.thr,
        'noise': args.noise,
        'sdm': args.sdm,
        'skip': args.skip
    }

    # Main analysis
    try:
        print("Starting analysis")
        success = run_model.analyze_directory(data_directory, parameters)
    except Exception as e:
        print(f"Error during analysis: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()