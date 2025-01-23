# Bird Identification

A bird audio identification tool designed to analyze recordings and generate a list of bird species detected using an AI model. Built with TensorFlow and Python, it operates within a Docker environment. The project is a work in progress and currently in a very preliminary stage.

## Setup

- `git clone`
- `cd bird-identification`
- `mkdir input && mkdir output && mkdir models`
- Place models to the `models` folder: BirdNET and Muuttolintujen kevät
- `docker compose up --build; docker compose down;`
- Access the running docker container:
  - `docker exec -ti bird-identification bash`
  - `cd app`
  - Run the script, see below

### Usage

- Place audio files to a subfolder of the `input` folder. The script will search the audio files here in this order, and will load files from the first one that contains at least one of them:
  1) ./subfolder/data
  2) ./subfolder/Data
  3. .subfolder
- Place *metadata.yaml* file in the subfolder. The file should contain the following fields:
  - `lat`: Latitude in decimal degrees
  - `lon`: Longitude in decimal degrees
  - `day_of_year`: Day of the year, 1-365/6
- Run the script with `python main.py --dir <subfolder>`
- Optional parameters:
    - `--thr`: Detection threshold as a decimal number between 0<>1, default 0.5
    - `--noise`: Include noise in the output, default False
    - `--sdm`: Use species distribution model to adjust confidence values, default False
    - `--skip`: Skip audio files that already have a corresponding result file, default False

#### Notes of usage

- Expects that
    - Audio filenames are in format [part1].[extension]
    - Extension is wav, mp3 or flac
    - If data files have already been generated with another application (e.g. BirdNET), they are in the same directory as the audio files and in format [part1].[part2].results.csv
    - Data files have columns: Start (s), End (s), Scientific name, Common name, Confidence, [Optional columns]
- If classification stops with message "Killed", try restarting the Docker container. It's unclear what causes this issue.

## Todo

- Save model run metadata, include it into the report
- Include both sdm and non-sdm predictions in the output
- add taxon MX codes to the output
- Check why comparison-audio files are sometimes split into 5, 6 or 7 segments
- Compare BirdNET, this model with SDM and this model without SDM. E.g. migration observations.
- How to handle multiple species being detected in the same time frame?
- Spectrograms
- Species commonness: how many % of observations from that area (+- 100 km) and time (+-10 days) are this species
- Should have:
  - Using handle_files from command line
  - Table of contents to the report
  - Normalize x-axis for all temporal charts. Get first and last time from the original data when it's loaded?
  - Organizing the repos: continue with this repo, include baim features. Then rethink whether this tool and analysis (Bart) tool should be bundled together. And how to manage web interface vs. desktop app.
  - Error handling when functions return None
  - Prepare for missing audio files & missing data files
  - Running analysis should save settings to a metadata file. Report should show those settings.
  - Unit testing
- Nice to have:
  - Handle file paths in a more consistent ways (directory path, file name, datetime from filename)
  - Histograms are not made for species with only few detections. However, <img> tag is generated for these on the result service. Would be elegant not to have broken image links, though they are not visible for users.


