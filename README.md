# Bird Identification

This repository provides tools for automated bird species detection from audio recordings and for generating quality control reports. It supports local processing and API-based workflows and is built on an AI model developed at the University of Jyväskylä as part of the [Muuttolintujen kevät -project](https://www.jyu.fi/en/research/muuttolintujen-kevat).

## Desktop App

The desktop application built from this repository is called **Sirkku** and is published by the [Finnish Biodiversity Information Facility (FinBIF / Suomen Lajitietokeskus)](https://laji.fi/about/9219). It allows users to identify Finnish bird species from audio recordings directly on their own computer, without any data leaving the device.

## Project Structure

- `shared/` — Shared code: classifier and functions
- `api/` — HTTP API (FastAPI)
- `cli/` — Command-line scripts for local analysis and report generation
- `app/` — Desktop application

## Features

- Analyzes audio recordings (WAV, MP3, FLAC) to detect bird species, either locally or via API
- Files are divided into smaller chunks based on chunk_size parameter, because the model has a limit on the input size. There chunks are then divided into segments of clip_dur seconds (currently fixed to 3 seconds), and overlap parameter defines how much of each segment is overlapped with the next segment.
- Uses species distribution and temporal modeling to improve detection accuracy
- Handles batch processing of multiple audio files
- Generates reports with species statistics and sample audio clips to help verifying the results
- Desktop application for users who prefer a graphical interface

## Setup

### Prerequisites

- Docker
- Git
- The following AI models:
  - BirdNET, included in this repository
  - BSG – Finnish Birds Model in keras format, available at [https://github.com/plauha/BSG_classifier_builder/tree/main/Run%20BSG%20models/models/Finland](https://github.com/plauha/BSG_classifier_builder/tree/main/Run%20BSG%20models/models/Finland)

### Installation

- `git clone`
- `cd bird-identification`
- Place models to the `/models` folder: BirdNET and Muuttolintujen kevät
- `docker compose up --build # start both cli and api`
- `docker compose up cli --build # start only cli`
- `docker compose up api --build # start only api`
- Desktop app has another setup, see [app/README.md](app/README.md)



### Running unit tests

From the host machine:

- `docker compose run --rm test`

## Usage

- For command line tool, see [cli/README.md](cli/README.md)
- For API, see [api/README.md](api/README.md)
- For desktop app, see [app/README.md](app/README.md)
