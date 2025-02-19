import pytest
import numpy as np
from datetime import datetime
import os
import yaml
from scripts.functions import (
    get_day_of_year_from_filename,
    get_date_and_time_from_filepath,
    threshold_filter,
    split_signal,
    pad,
    make_output_file_path,
    get_audio_file_names,
    read_metadata
)

# Test get_day_of_year_from_filename
class TestGetDayOfYear:
    @pytest.mark.parametrize("filename,expected", [
        ("20240527_200000.wav", 148),  # May 27, 2024
        ("prefix_20240406_015900.wav", 97),  # April 6, 2024
        ("invalid_file.wav", None),
        ("2024_01_01.wav", None),
    ])
    def test_get_day_of_year(self, filename, expected):
        result = get_day_of_year_from_filename(filename)
        assert result == expected

# Test get_date_and_time_from_filepath
class TestGetDateAndTime:
    @pytest.mark.parametrize("filepath,expected", [
        ("/path/to/20240527_200000.wav", ("20240527", "2000")),
        ("/path/to/prefix_20240406_015900.wav", ("20240406", "0159")),
        ("/path/to/invalid_file.wav", None),
        ("/path/to/2024_01_01.wav", None),
    ])
    def test_get_date_and_time(self, filepath, expected):
        result = get_date_and_time_from_filepath(filepath)
        assert result == expected

# Test threshold_filter
class TestThresholdFilter:
    def test_threshold_filter_basic(self):
        # Create sample data
        predictions = np.array([[0.3, 0.7, 0.4],
                              [0.8, 0.2, 0.6]])
        timestamps = np.array([0, 1])
        threshold = 0.5

        filtered_preds, class_indices, filtered_times = threshold_filter(
            predictions, timestamps, threshold
        )

        # Check results
        assert len(filtered_preds) == 3  # Should have 3 predictions above threshold
        assert all(p >= threshold for p in filtered_preds)
        assert len(class_indices) == 3
        assert len(filtered_times) == 3

    def test_threshold_filter_empty(self):
        predictions = np.array([[0.3, 0.2, 0.4],
                              [0.1, 0.2, 0.3]])
        timestamps = np.array([0, 1])
        threshold = 0.5

        filtered_preds, class_indices, filtered_times = threshold_filter(
            predictions, timestamps, threshold
        )

        assert len(filtered_preds) == 0
        assert len(class_indices) == 0
        assert len(filtered_times) == 0

# Test signal processing functions
class TestSignalProcessing:
    def test_pad(self):
        signal = np.ones(24000)  # 0.5s at 48kHz
        x1, x2 = 0, 0.5
        target_len = 48000  # 1s
        sr = 48000

        padded = pad(signal, x1, x2, target_len, sr)
        
        assert len(padded) == target_len
        assert np.sum(padded[:24000]) == len(signal)  # First half should be ones
        assert np.sum(padded[24000:]) == 0  # Second half should be zeros

    def test_split_signal(self):
        # Create 2-second signal
        sample_rate = 48000
        signal = np.ones(2 * sample_rate)
        chunk_duration = 1.0
        overlap_duration = 0.5

        chunks = split_signal(signal, sample_rate, chunk_duration, overlap_duration)

        # We get 4 chunks because:
        # - Signal length is 2.0s
        # - Each chunk is 1.0s
        # - Step size is 0.5s (chunk_duration - overlap_duration)
        # - This results in chunks starting at 0s, 0.5s, 1.0s, and 1.5s
        assert len(chunks) == 4
        assert all(len(chunk) == int(chunk_duration * sample_rate) for chunk in chunks)
        
        # Verify that the last chunk is padded with zeros
        assert np.sum(chunks[-1]) == 0.5 * sample_rate  # Only half of the last chunk should be ones

# Test file operations
class TestFileOperations:
    def test_make_output_file_path(self, tmp_path):
        output_dir = str(tmp_path)
        file_name = "test_audio.wav"
        
        # Test non-existent file
        path, exists = make_output_file_path(output_dir, file_name)
        assert path == f"{output_dir}/test_audio.Muuttolinnut.results.csv"
        assert exists is False

        # Create the file and test again
        with open(path, 'w') as f:
            f.write("")
        
        path, exists = make_output_file_path(output_dir, file_name)
        assert exists is True

    def test_get_audio_file_names(self, tmp_path):
        # Create test files
        valid_files = ["test1.wav", "test2.mp3", "test3.flac"]
        invalid_files = ["test4.txt", "test5.jpg"]
        
        for fname in valid_files + invalid_files:
            with open(os.path.join(tmp_path, fname), 'w') as f:
                f.write("")

        files = get_audio_file_names(str(tmp_path))
        
        assert len(files) == len(valid_files)
        assert all(f in files for f in valid_files)
        assert all(f not in files for f in invalid_files)

# Test metadata handling
class TestMetadata:
    def test_read_valid_metadata(self, tmp_path):
        metadata_content = {
            "lat": 60.1699,
            "lon": 24.9384,
            "day_of_year": 1
        }
        
        with open(os.path.join(tmp_path, "metadata.yaml"), 'w') as f:
            yaml.dump(metadata_content, f)

        result = read_metadata(str(tmp_path))
        assert result == metadata_content

    def test_read_invalid_metadata(self, tmp_path):
        # Test missing required fields
        with open(os.path.join(tmp_path, "metadata.yaml"), 'w') as f:
            yaml.dump({"lat": 60.1699}, f)
        
        assert read_metadata(str(tmp_path)) is None

        # Test invalid latitude
        with open(os.path.join(tmp_path, "metadata.yaml"), 'w') as f:
            yaml.dump({"lat": 91, "lon": 0}, f)
        
        assert read_metadata(str(tmp_path)) is None

        # Test invalid longitude
        with open(os.path.join(tmp_path, "metadata.yaml"), 'w') as f:
            yaml.dump({"lat": 0, "lon": 181}, f)
        
        assert read_metadata(str(tmp_path)) is None

    def test_read_nonexistent_metadata(self, tmp_path):
        # Test with directory that exists but no metadata file
        assert read_metadata(str(tmp_path)) is None

        # Test with nonexistent directory
        assert read_metadata("/nonexistent/path") is None 