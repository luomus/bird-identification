# Script to be accessed from a command line, to make a report.

#!/usr/bin/env python3

import argparse
import sys
import os
from pydantic_parameters import ReportParameters
import handle_files
from typing import Optional, Dict
import functions


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate report of analyzed audio files.'
    )
    
    # Add required arguments
    parser.add_argument(
        '--dir',
        type=str,
        required=True,
        help='Directory that contains the audio and result files'
    )
    parser.add_argument(
        '--thr',
        type=float,
        default=0.5,
        help='Threshold for species prediction filtering. Minimum 0, maximum 1, default 0.5.'
    )
    parser.add_argument(
        '--padding',
        type=int,
        default=1,
        help='Padding in seconds for example audio files. Minimum 0, maximum 10, default 1.'
    )
    parser.add_argument(
        '--examples',
        type=int,
        default=5,
        help='Number of example audio files to pick for each species. Minimum 5, maximum 50, default 5.'
    )

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # Handle --help or invalid arguments
        print("Error: Invalid arguments", file=sys.stderr)
        return

    # Check that directory exists
    data_directory = "../input/" + args.dir
    if not os.path.exists(data_directory):
        print(f"Error: Directory {data_directory} does not exist", file=sys.stderr)
        return

    # Create and validate parameters
    try:
        parameters = ReportParameters(
            directory=data_directory,
            threshold=args.thr,
            padding=args.padding,
            examples=args.examples
        )
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return

    # Main report generation
    try:
        print("Starting report generation")
        success = handle_files.handle_files(parameters.directory, parameters.to_dict())
    except Exception as e:
        print(f"Error during analysis: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()