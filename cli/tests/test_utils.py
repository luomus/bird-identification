import pytest
import os
import yaml
from cli.utils import (
    get_day_of_year_from_filename,
    get_date_and_time_from_filepath,
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

