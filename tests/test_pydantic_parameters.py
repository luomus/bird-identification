import pytest
from pathlib import Path
from pydantic import ValidationError
from scripts.pydantic_parameters import BaseParameters, Metadata, AnalysisParameters, ReportParameters

# Fixture for temporary directory
@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return str(tmp_path)

# Test BaseParameters
class TestBaseParameters:
    def test_valid_parameters(self, temp_dir):
        params = BaseParameters(directory=temp_dir)
        assert params.directory == temp_dir
        assert params.threshold == 0.5

    def test_invalid_directory(self):
        with pytest.raises(ValidationError):
            BaseParameters(directory="/nonexistent/path")

    def test_valid_directory(self):
        params = BaseParameters(directory="./input")
        assert params.directory == "input"

    def test_invalid_threshold(self, temp_dir):
        with pytest.raises(ValidationError):
            BaseParameters(directory=temp_dir, threshold=1.5)

        with pytest.raises(ValidationError):
            BaseParameters(directory=temp_dir, threshold=-0.1)

    def test_valid_threshold(self):
        threshold_to_test = 0.9
        params = BaseParameters(directory=".", threshold=threshold_to_test)
        assert params.threshold == threshold_to_test

# Test Metadata
class TestMetadata:
    def test_valid_metadata(self):
        metadata = Metadata(lat=60.1699, lon=24.9384, day_of_year=1)
        assert metadata.lat == 60.1699
        assert metadata.lon == 24.9384
        assert metadata.day_of_year == 1

    def test_invalid_day_of_year(self):
        with pytest.raises(ValidationError):
            Metadata(lat=60.1699, lon=24.9384, day_of_year=0)

        with pytest.raises(ValidationError):
            Metadata(lat=60.1699, lon=24.9384, day_of_year=367)

    def test_invalid_coordinates(self):
        with pytest.raises(ValidationError):
            Metadata(lat=91.0, lon=0.0)

        with pytest.raises(ValidationError):
            Metadata(lat=-91.0, lon=0.0)

        with pytest.raises(ValidationError):
            Metadata(lat=0.0, lon=181.0)

        with pytest.raises(ValidationError):
            Metadata(lat=0.0, lon=-181.0)

# Test AnalysisParameters
class TestAnalysisParameters:
    def test_valid_analysis_parameters(self, temp_dir):
        params = AnalysisParameters(
            directory=temp_dir,
            metadata=Metadata(lat=60.1699, lon=24.9384, day_of_year=1),
            threshold=0.6,
            noise=True,
            sdm=True,
            skip=True,
            chunk_size=120
        )
        assert params.directory == temp_dir
        assert params.threshold == 0.6
        assert params.noise is True
        assert params.sdm is True
        assert params.skip is True
        assert params.chunk_size == 120

    def test_invalid_chunk_size(self, temp_dir):
        with pytest.raises(ValidationError):
            AnalysisParameters(
                directory=temp_dir,
                metadata=Metadata(lat=60.1699, lon=24.9384, day_of_year=1),
                chunk_size=59
            )

    def test_to_dict(self, temp_dir):
        params = AnalysisParameters(
            directory=temp_dir,
            metadata=Metadata(lat=60.1699, lon=24.9384, day_of_year=1)
        )
        result = params.to_dict()
        assert result["threshold"] == 0.5
        assert result["noise"] is False
        assert result["sdm"] is False
        assert result["skip"] is False
        assert result["metadata"]["lat"] == 60.1699
        assert result["metadata"]["lon"] == 24.9384
        assert result["metadata"]["day_of_year"] == 1

# Test ReportParameters
class TestReportParameters:
    def test_valid_report_parameters(self, temp_dir):
        params = ReportParameters(
            directory=temp_dir,
            threshold=0.7,
            padding=2,
            examples=10
        )
        assert params.directory == temp_dir
        assert params.threshold == 0.7
        assert params.padding == 2
        assert params.examples == 10

    def test_invalid_padding(self, temp_dir):
        with pytest.raises(ValidationError):
            ReportParameters(directory=temp_dir, padding=11)

        with pytest.raises(ValidationError):
            ReportParameters(directory=temp_dir, padding=-1)

    def test_invalid_examples(self, temp_dir):
        with pytest.raises(ValidationError):
            ReportParameters(directory=temp_dir, examples=4)

        with pytest.raises(ValidationError):
            ReportParameters(directory=temp_dir, examples=51)

    def test_to_dict(self, temp_dir):
        params = ReportParameters(directory=temp_dir)
        result = params.to_dict()
        assert result["threshold"] == 0.5
        assert result["padding"] == 1
        assert result["examples"] == 5 