from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Tuple
import functions
from pathlib import Path


class BaseParameters(BaseModel):
    """Base class for parameters validation."""
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
    """Metadata for audio analysis."""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    day_of_year: int = Field(..., ge=1, le=366, description="Day of year")


class AnalysisParameters(BaseParameters):
    """Parameters for model analysis."""
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
    """Parameters for report generation."""
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