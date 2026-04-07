import pytest

from shared.classifier_config import (
    ClassifierConfig,
    RawConfig,
    SpectrogramConfig,
    ResultFormat,
    LogPreprocessing,
    StandardizePreprocessing,
    CenterPreprocessing,
)


class TestClassifierConfig:

    def test_defaults(self):
        config = ClassifierConfig()

        assert config.model_path is None
        assert config.sample_rate == 48000
        assert config.requires_spectrogram is False
        assert config.result_format == ResultFormat.PROBABILITIES
        assert config.preprocessing == []

    def test_clip_duration_raw(self):
        config = ClassifierConfig(raw_config=RawConfig(clip_duration=5))

        assert config.clip_duration == 5

    def test_clip_duration_spectrogram(self):
        config = ClassifierConfig(
            requires_spectrogram=True,
            spectrogram_config=SpectrogramConfig(input_height=512, hop_length=768),
            sample_rate=48000,
        )

        assert config.clip_duration == pytest.approx(8.192)

    def test_from_dict_minimal(self):
        config = ClassifierConfig.from_dict({})

        assert config.sample_rate == 48000
        assert config.result_format == ResultFormat.PROBABILITIES

    def test_from_dict_with_sample_rate(self):
        config = ClassifierConfig.from_dict({"sample_rate": 24000})

        assert config.sample_rate == 24000

    def test_from_dict_with_raw_config(self):
        config = ClassifierConfig.from_dict({
            "raw_config": {"clip_duration": 5, "requires_birdnet": True},
        })

        assert config.raw_config.clip_duration == 5
        assert config.raw_config.requires_birdnet is True

    def test_from_dict_with_spectrogram_config(self):
        config = ClassifierConfig.from_dict({
            "requires_spectrogram": True,
            "spectrogram_config": {"n_fft": 2048, "fmin": 500, "fmax": 12000},
        })

        assert config.requires_spectrogram is True
        assert config.spectrogram_config.n_fft == 2048
        assert config.spectrogram_config.fmin == 500
        assert config.spectrogram_config.fmax == 12000

    def test_from_dict_with_preprocessing(self):
        config = ClassifierConfig.from_dict({
            "preprocessing": [
                {"type": "log", "base": 10},
                {"type": "standardize"},
                {"type": "center", "method": "median", "axis": 0},
            ],
        })

        assert len(config.preprocessing) == 3
        assert isinstance(config.preprocessing[0], LogPreprocessing)
        assert config.preprocessing[0].base == 10
        assert isinstance(config.preprocessing[1], StandardizePreprocessing)
        assert isinstance(config.preprocessing[2], CenterPreprocessing)
        assert config.preprocessing[2].method == "median"

    def test_from_dict_with_logits_result_format(self):
        config = ClassifierConfig.from_dict({"result_format": "logits"})

        assert config.result_format == ResultFormat.LOGITS

