from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Tuple
import functions
from pathlib import Path


class BaseParameters(BaseModel):
    """Base parameter validation for audio analysis tasks.
    
    This class provides common validation logic for directory paths and confidence
    thresholds used across different analysis and reporting stages. 
    All parameter classes inherit from this base class.
    """
    directory: str
    threshold: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Threshold for species prediction filtering"
    )

    @validator('directory')
    def validate_directory(cls, v):
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Directory '{v}' does not exist")
        if not path.is_dir():
            raise ValueError(f"Path '{v}' is not a directory")
        return str(path)


class Metadata(BaseModel):
    """Geographic and temporal metadata for audio analysis.
    
    This model is used as a nested component within AnalysisParameters to provide
    data that remains constant across different analysis.
    """
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    day_of_year: int = Field(..., ge=1, le=366, description="Day of year")


class AnalysisParameters(BaseParameters):
    """Parameters for the initial audio analysis and species detection phase.
    
    This class extends BaseParameters to include settings for the audio
    processing pipeline.

    Example:
        ```python
        params = AnalysisParameters(
            directory="path/to/audio",
            metadata=Metadata(lat=42.0, lon=-71.0, day_of_year=180),
            threshold=0.6,
            noise=True
        )
        ```
    """
    metadata: Metadata
    noise: bool = Field(
        default=False,
        description="Ignore non-bird predictions"
    )
    sdm: bool = Field(
        default=False,
        description="Enable species distribution model adjustments"
    )
    skip: bool = Field(
        default=False,
        description="Skip analyzing if output file exists"
    )
    chunk_size: int = Field(
        default=600,
        ge=60,
        description="Chunk size in seconds"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary format."""
        return {
            'threshold': self.threshold,
            'noise': self.noise,
            'sdm': self.sdm,
            'skip': self.skip,
            'metadata': self.metadata.dict()
        }


class ReportParameters(BaseParameters):
    """Parameters for generating analysis reports with audio examples.
    
    This class extends BaseParameters to customize the post-analysis report.

    Example:
        ```python
        params = ReportParameters(
            directory="path/to/results",
            threshold=0.7,
            padding=2,
            examples=10
        )
        ```
    """
    padding: int = Field(
        default=1,
        ge=0,
        le=10,
        description="Padding in seconds for example audio files"
    )
    examples: int = Field(
        default=5,
        ge=5,
        le=50,
        description="Number of example audio files per species"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary format."""
        return {
            'threshold': self.threshold,
            'padding': self.padding,
            'examples': self.examples
        } 