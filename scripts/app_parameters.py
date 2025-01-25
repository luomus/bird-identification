from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import functions


@dataclass
class BaseParameters:
    """Base class for parameters validation and storage."""
    directory: str
    threshold: float = 0.5

    @staticmethod
    def validate_directory(directory: str) -> Tuple[Optional[str], Optional[str]]:
        """Validate directory path.
        Returns: (validated_path, error_message)"""
        if directory is None:
            return None, "Directory path cannot be empty"

        data_directory, error_message = functions.get_data_directory(directory)
        if error_message:
            return None, error_message

        return data_directory, None

    @staticmethod
    def validate_threshold(threshold: Any) -> Tuple[float, Optional[str]]:
        """Validate threshold value.
        Returns: (validated_value, warning_message)"""
        default_value = 0.5
        
        # Handle type conversion
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return default_value, f"Invalid threshold value '{threshold}', using default {default_value}"

        # Handle range validation
        if not (0 <= threshold <= 1):
            return default_value, f"Threshold must be between 0 and 1, using default {default_value}"
            
        return threshold, None


@dataclass
class AnalysisParameters(BaseParameters):
    """Parameters for model analysis."""
    noise: bool = False
    sdm: bool = False
    skip: bool = False

    @staticmethod
    def validate_boolean(value: Any, param_name: str) -> Tuple[bool, Optional[str]]:
        """Validate boolean parameters.
        Returns: (validated_value, warning_message)"""
        if isinstance(value, bool):
            return value, None
        
        return False, f"Invalid {param_name} value '{value}', using default False"

    @classmethod
    def create(cls, directory: str, threshold: Any = 0.5, 
               noise: Any = False, sdm: Any = False, 
               skip: Any = False) -> Tuple['ModelAnalysisParameters', list[str]]:
        """Factory method to create and validate parameters."""
        warnings = []
        
        # Validate directory (required parameter)
        valid_dir, dir_error = cls.validate_directory(directory)
        if dir_error:
            raise ValueError(dir_error)
        
        # Validate threshold
        valid_threshold, thr_warning = cls.validate_threshold(threshold)
        if thr_warning:
            warnings.append(thr_warning)
            
        # Validate boolean parameters
        valid_noise, noise_warning = cls.validate_boolean(noise, "noise")
        if noise_warning:
            warnings.append(noise_warning)
            
        valid_sdm, sdm_warning = cls.validate_boolean(sdm, "sdm")
        if sdm_warning:
            warnings.append(sdm_warning)
            
        valid_skip, skip_warning = cls.validate_boolean(skip, "skip")
        if skip_warning:
            warnings.append(skip_warning)

        return cls(
            directory=valid_dir,
            threshold=valid_threshold,
            noise=valid_noise,
            sdm=valid_sdm,
            skip=valid_skip
        ), warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary format."""
        return {
            'threshold': self.threshold,
            'noise': self.noise,
            'sdm': self.sdm,
            'skip': self.skip
        }


@dataclass
class ReportParameters(BaseParameters):
    """Parameters for report."""
    padding: int = 1
    examples: int = 5

    @staticmethod
    def validate_padding(padding: int) -> Tuple[int, Optional[str]]:
        """Validate padding value.
        Returns: (validated_value, warning_message)"""
        default_value = 1
        
        try:
            padding = int(padding)
        except (TypeError, ValueError):
            return default_value, f"Invalid padding value '{padding}', using default {default_value}"

        if padding < 0:
            return 0, f"Padding must be between 0 and 10, using 0"
        if padding > 10:
            return 10, f"Padding must be between 0 and 10, using 10"

        return padding, None

    @staticmethod
    def validate_examples(examples: int) -> Tuple[int, Optional[str]]:
        """Validate examples value.
        Returns: (validated_value, warning_message)"""
        default_value = 5

        try:
            examples = int(examples)
        except (TypeError, ValueError):
            return default_value, f"Invalid examples value '{examples}', using default {default_value}"
        
        if examples < 5:
            return 5, f"Examples must be at least 5, using default {default_value}"
        if examples > 50:
            return 50, f"Examples must be at most 50, using default {default_value}"

        return examples, None

    @classmethod
    def create(cls, directory: str, threshold: Any = 0.5,
               padding: Any = 1, examples: Any = 5) -> Tuple['FileAnalysisParameters', list[str]]:
        """Factory method to create and validate parameters."""
        warnings = []
        
        # Validate directory (required parameter)
        valid_dir, dir_error = cls.validate_directory(directory)
        if dir_error:
            raise ValueError(dir_error)
        
        # Validate threshold
        valid_threshold, thr_warning = cls.validate_threshold(threshold)
        if thr_warning:
            warnings.append(thr_warning)
            
        # Validate padding
        valid_padding, padding_warning = cls.validate_padding(padding)
        if padding_warning:
            warnings.append(padding_warning)
            
        # Validate examples
        valid_examples, examples_warning = cls.validate_examples(examples)
        if examples_warning:
            warnings.append(examples_warning)

        return cls(
            directory=valid_dir,
            threshold=valid_threshold,
            padding=valid_padding,
            examples=valid_examples
        ), warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary format."""
        return {
            'threshold': self.threshold,
            'padding': self.padding,
            'examples': self.examples
        } 