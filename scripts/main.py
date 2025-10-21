# Script to be accessed from a command line, to analyze audio files.

#!/usr/bin/env python3

import argparse
import sys
import os
import run_model
from scripts.pydantic_parameters import AnalysisParameters, Metadata
import scripts.functions

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
        help='Directory that contains the audio files. Required.'
    )
    parser.add_argument(
        '--thr',
        type=float,
        default=0.5,
        help='Threshold for species prediction filtering. Optional, default 0.5.'
    )
    parser.add_argument(
        '--overlap',
        type=float,
        default=1,
        help='Overlap in seconds. Optional, default 1.'
    )
    parser.add_argument(
        '--noise',
        action='store_true',
        help='Ignore non-bird predictions, e.g. engine noise. Optional, default False.'
    )
    parser.add_argument(
        '--sdm',
        action='store_true',
        help='Enable species distribution model adjustments. Optional, default False.'
    )
    parser.add_argument(
        '--skip',
        action='store_true',
        help='Whether to skip analyzing a file if output file already exists. Optional, default False.'
    )
    parser.add_argument(
        '--chunk_size',
        type=int,
        default=600,
        help='Segment chunk size in seconds. Optional, default 600.'
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

    # Read metadata first
    metadata = functions.read_metadata(data_directory)
    if metadata is None:
        print(f"Error: Proper metadata file not found at {data_directory}", file=sys.stderr)
        return

    # Create and validate parameters
    try:
        metadata_model = Metadata(**metadata)
        parameters = AnalysisParameters(
            directory=data_directory,
            threshold=args.thr,
            noise=args.noise,
            sdm=args.sdm,
            skip=args.skip,
            overlap=args.overlap,
            chunk_size=args.chunk_size,
            metadata=metadata_model
        )
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        raise

    # Main analysis
    try:
        print("Starting analysis")
        success = run_model.analyze_directory(parameters.directory, parameters.to_dict())
    except Exception as e:
        print(f"Error: An error occurred during analysis: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()