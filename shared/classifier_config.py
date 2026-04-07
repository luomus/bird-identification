from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, List, Literal


class ResultFormat(Enum):
    PROBABILITIES = "probabilities"
    LOGITS = "logits"

@dataclass
class RawConfig:
    clip_duration: Union[int, float] = 3
    requires_birdnet: bool = False
    birdnet_model_path: Optional[str] = None

@dataclass
class SpectrogramConfig:
    n_fft: int = 1024
    hop_length: int = 768
    n_mels: int = 128
    fmin: Optional[int] = None
    fmax: Optional[int] = None
    log_scale: bool = True
    input_height: int = 512
    input_width: int = 128
    channels_first: bool = True

@dataclass
class LogPreprocessing:
    type: Literal["log"]
    base: int = 10
    epsilon: float = 1e-6

@dataclass
class StandardizePreprocessing:
    type: Literal["standardize"]

@dataclass
class CenterPreprocessing:
    type: Literal["center"]
    method: Literal["mean", "median"] = "mean"
    axis: int = 0

@dataclass
class ClipPreprocessing:
    type: Literal["clip"]
    range: tuple[float, float]

PreprocessingStep = Union[
    LogPreprocessing,
    StandardizePreprocessing,
    CenterPreprocessing,
    ClipPreprocessing,
]

def preprocessing_step_from_dict(d: dict) -> PreprocessingStep:
    step_type = d.get("type")

    if step_type == "log":
        return LogPreprocessing(**d)

    elif step_type == "standardize":
        return StandardizePreprocessing(**d)

    elif step_type == "center":
        return CenterPreprocessing(**d)

    elif step_type == "clip":
        return ClipPreprocessing(**d)

    else:
        raise ValueError(f"Unknown preprocessing type: {step_type}")

@dataclass
class ClassifierConfig:
    model_path: Optional[str] = None
    sample_rate: Union[int, float] = 48000
    tflite_threads: int = 1 # can be as high as number of CPUs

    requires_spectrogram: bool = False
    raw_config: RawConfig = field(default_factory=RawConfig)
    spectrogram_config: SpectrogramConfig = field(default_factory=SpectrogramConfig)

    preprocessing: List[PreprocessingStep] = field(default_factory=list)

    result_format: ResultFormat = ResultFormat.PROBABILITIES

    @property
    def clip_duration(self) -> float:
        if self.requires_spectrogram:
            return self.spectrogram_config.input_height * (self.spectrogram_config.hop_length / self.sample_rate)
        else:
            return self.raw_config.clip_duration

    @classmethod
    def from_dict(cls, d: dict) -> "ClassifierConfig":
        raw_config = RawConfig(**d.get("raw_config", {}))
        spectrogram_config = SpectrogramConfig(**d.get("spectrogram_config", {}))
        preprocessing = [
            preprocessing_step_from_dict(p)
            for p in d.get("preprocessing", [])
        ]
        result_format = ResultFormat(d.get("result_format", "probabilities"))

        return cls(
            **{
                **d,
                "raw_config": raw_config,
                "spectrogram_config": spectrogram_config,
                "preprocessing": preprocessing,
                "result_format": result_format
            }
        )
