# Usage

## Identifying species locally

This analyzes audio files and generates tabular text files containing the identifications, one file for each audio file.

- Place audio files to a folder under `/input`, for example `/input/my_backyard_2025-01`.
- Place `metadata.yaml` file in the same folder. This contains information that is shared by all the files. Example format:

```yaml
lat: 60.123
lon: 24.123 
day_of_year: 152 # Note: this will be overridden if audio file names include a date
```

- Access the CLI container:
  - `docker exec -ti bird-identification-cli bash`
  - `python -m cli.main --dir <subfolder>`
- Or run a one-off command:
  - `docker compose run --rm cli python -m cli.main --dir <subfolder>`
- Optional parameters:
  - `--thr`: Detection threshold as a decimal number between 0<>1, default 0.5
  - `--noise`: Include noise in the output, default False
  - `--sdm`: Use species distribution model to adjust confidence values, default False
  - `--skip`: Skip audio files that already have a corresponding result file, default False
  - `--overlap`: Overlap of segments to be analyzed in seconds, default 1.
  - `--chunk_size`: Audio files are cut into chunks for analysis. This defines the size in seconds, default 600.

### Note

- Expects that
  - Audio filenames are in format `[part1].[extension]`
  - Extension is `wav`, `mp3` or `flac`, case-insensitive
- If classification stops with message "Killed", try restarting the Docker container. It's unclear what causes this issue.
- The model and/or classifier has limitations:
  - Segments can't be too long. 10 minutes seem to work fine, 30 minutes are too long.
  - Overlap can't be too high. 1 second works fine, 2 seconds doesn't. Longer overlap leads to "Killed" message.

## Generating validation report

This reads tabular files containing species identifications, and generates an HTML report with example audio files for validation, and statistics and charts of the species.

- First do species identification, see above. You can also use BirdNET to do the identifications (use csv export format.)
- Validation report generation expects that:
  - Data files are in the same directory as the audio files and in format `[part1].[part2].results.csv`
  - Data files have columns: `Start (s), End (s), Scientific name, Common name, Confidence, [Optional columns]`
- Run the script with `python -m cli.main_report --dir <subfolder>`
- Optional parameters:
  - `--thr`: Detection threshold as a decimal number between 0<>1, default 0.5
  - `--padding`: Padding in seconds for example audio files, default 1.
  - `--examples`: Number of example audio files to pick for each species, minimum 5, default 5.

# Todo

- Analysis
  - Include inference details in the analysis result file, or at least identify the inference file?
  - Refactor to handle settings in a centralized way, so that adding new parameters is easier
  - Add clip_dur as a parameter
  - Include both sdm and non-sdm predictions in the output
  - Add taxon MX codes to the output
  - Check why comparison-audio files are sometimes split into 5, 6 or 7 segments
- Report
  - If data from one day only, don't create date histogram
  - Include inference metadata into the report, so that it can be shared independently. But what to do if there are multiple inference files?
  - Species commonness: how many % of observations from that area (+- 100 km) and time (+-10 days) are this species
  - Normalize x-axis for all temporal charts. Get first and last time from the original data when it's loaded?
  - Histograms are not made for species with only few detections. However, <img> tag is generated for these on the result service. Would be elegant not to have broken image links, though they are not visible for users.
- Misc
  - Error handling when functions return None
  - More unit testing
  - Handle file paths in a more consistent ways (directory path, file name, datetime from filename)
