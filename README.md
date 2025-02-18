# Bird Identification

A bird audio identification tool designed to analyze recordings and generate a list of bird species detected using an AI model. Built with TensorFlow and Python, it operates within a Docker environment. The project is a work in progress and currently in a very preliminary stage.

## Features

- Analyzes audio recordings (WAV, MP3, FLAC) to detect bird species
- Uses species distribution and temporal modeling to improve detection accuracy
- Handles batch processing of multiple audio files
- Generates reports with species statistics and sample audio clips to help verifying the results

## Setup

### Prerequisites

- Docker
- Git
- The following AI models (available on request):
  - BirdNET
  - Muuttolintujen kevät

### Installation

- `git clone`
- `cd bird-identification`
- Place models to the `/models` folder: BirdNET and Muuttolintujen kevät
- `docker compose up --build; docker compose down;`
- Access the running docker container:
  - `docker exec -ti bird-identification bash`
  - Run the scripts, see below

## Usage

### Identifying species

This analyzes audio files and generates tabular text files containing the identifications, one file for each audio file.

- Place audio files to a subfolder of the `/input` folder, for example `/input/my_backyard_2025-01`. The script will search the audio files here in this order, and will load files from the first one that contains at least one of them:
  1) `./subfolder/data`
  2) `./subfolder/Data`
  3. `.subfolder`
- Place `metadata.yaml` file in the subfolder. Example format:

```yaml
lat: 60.123
lon: 24.123 
day_of_year: 152
```
- Run the script with `python main.py --dir <subfolder>`
- Optional parameters:
  - `--thr`: Detection threshold as a decimal number between 0<>1, default 0.5
  - `--noise`: Include noise in the output, default False
  - `--sdm`: Use species distribution model to adjust confidence values, default False
  - `--skip`: Skip audio files that already have a corresponding result file, default False

#### Note

- Expects that
  - Audio filenames are in format `[part1].[extension]`
  - Extension is `wav`, `mp3` or `flac`
  - If data files have already been generated with another application (e.g. BirdNET), they are in the same directory as the audio files and in format `[part1].[part2].results.csv`
  - Data files have columns: `Start (s), End (s), Scientific name, Common name, Confidence, [Optional columns]`
- If classification stops with message "Killed", try restarting the Docker container. It's unclear what causes this issue.

### Generating validation report

This reads tabular files containing species identifications, and generates an HTML report with example audio files for validation, and statistics and charts of the species.

- First do species identification, see above
- Run the script with `python main_report.py --dir <subfolder>`
- Optional parameters:
  - `--thr`: Detection threshold as a decimal number between 0<>1, default 0.5
  - `--padding`: Padding in seconds for example audio files, default 1.
  - `--examples`: Number of example audio files to pick for each species, minimum 5, default 5.

### Identifying species using API

#### /classify

A bare minimum call with mandatory `latitude` and `longitude` parameters looks like this:

```bash
curl -X POST "http://localhost:8000/classify?latitude=60.1699&longitude=24.9384" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@input/suomenoja/Suomenoja_20240517_000000.flac"
```

Call with all parameters:

```bash
curl -X POST "http://localhost:8000/classify?latitude=60.1699&longitude=24.9384&threshold=0.5&include_sdm=True&include_noise=True&day_of_year=1&chunk_size=500" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@input/suomenoja/Suomenoja_20240517_000000.flac"
```

## Todo

- Next:
  - How to handle multiple species being detected in the same time frame?
- Maybe later:
  - Include inference metadata into the report, so that it can be shared independently. But what to do if there are multiple inference files?
  - Include both sdm and non-sdm predictions in the output
  - Add taxon MX codes to the output
  - Check why comparison-audio files are sometimes split into 5, 6 or 7 segments
  - Spectrograms
  - Species commonness: how many % of observations from that area (+- 100 km) and time (+-10 days) are this species
  - Normalize x-axis for all temporal charts. Get first and last time from the original data when it's loaded?
  - Organizing the repos: continue with this repo, include baim features. Then rethink whether this tool and analysis (Bart) tool should be bundled together. And how to manage web interface vs. desktop app.
  - Error handling when functions return None
  - Prepare for missing audio files & missing data files
  - Running analysis should save settings to a metadata file. Report should show those settings.
  - Unit testing
  - Handle file paths in a more consistent ways (directory path, file name, datetime from filename)
  - Histograms are not made for species with only few detections. However, <img> tag is generated for these on the result service. Would be elegant not to have broken image links, though they are not visible for users.


