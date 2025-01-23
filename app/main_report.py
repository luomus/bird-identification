# Script to be accessed from a command line, to make a report.

#!/usr/bin/env python3

import argparse
import sys
import os
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
        help='Threshold for species prediction filtering.'
    )
    parser.add_argument(
        '--padding',
        type=int,
        default=1,
        help='Padding in seconds for example audio files. Default 1.'
    )
    parser.add_argument(
        '--examples',
        type=int,
        default=5,
        help='Number of example audio files to pick for each species. Minimum 5, default 5.'
    )

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # Handle --help or invalid arguments
        return

    # Validate
    # Check if directory exists
    data_directory = functions.get_data_directory(args.dir)
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
        'padding_seconds': args.padding,
        'example_count': args.examples
    }

    # Main report generation
    try:
        print("Starting report generation")
        success = handle_files.handle_files(data_directory, parameters)
    except Exception as e:
        print(f"Error during analysis: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()