# Script to be accessed from a command line, to analyze audio files.

#!/usr/bin/env python3

import argparse
import sys
import run_model


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

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # Handle --help or invalid arguments
        print("Error: Invalid arguments", file=sys.stderr)
        return

    # Create and validate parameters
    try:
        parameters, warnings = run_model.AnalysisParameters.create(
            directory=args.dir,
            threshold=args.thr,
            noise=args.noise,
            sdm=args.sdm,
            skip=args.skip
        )
        
        # Print any warnings about parameter adjustments
        for warning in warnings:
            print(f"Warning: {warning}", file=sys.stderr)

    except ValueError as e:
        print(f"Error: Value error: {str(e)}", file=sys.stderr)
        return

    # Main analysis
    try:
        print("Starting analysis")
        success = run_model.analyze_directory(parameters.directory, parameters.to_dict())
    except Exception as e:
        print(f"Error: An error occurred during analysis: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()