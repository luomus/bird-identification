import pytest
import numpy as np
import pandas as pd
from shared.functions import (
    threshold_filter,
    second_stage_threshold_filter,
    split_signal,
    pad,
    calibrate,
    predictions_to_dataframe,
    log_transform,
    standardize_transform,
    center_transform,
    clip_transform,
)


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


class TestCalibrate:

    def test_output_between_zero_and_one(self):
        predictions = np.array([0.3, 0.7, 0.9])
        params = np.array([
            [0.0, 1.0],
            [0.0, 1.0],
            [0.0, 1.0],
        ])

        result = calibrate(predictions, params)

        assert all(0 <= p <= 1 for p in result)


class TestSecondStageThresholdFilter:

    def test_filters_below_threshold(self):
        predictions = np.array([0.3, 0.8, 0.6, 0.1])
        class_indices = np.array([0, 1, 2, 3])
        timestamps = np.array([0.0, 3.0, 6.0, 9.0])

        filtered_preds, filtered_indices, filtered_times = second_stage_threshold_filter(
            predictions, class_indices, timestamps, threshold=0.5
        )

        assert list(filtered_preds) == [0.8, 0.6]
        assert list(filtered_indices) == [1, 2]
        assert list(filtered_times) == [3.0, 6.0]

    def test_nothing_above_threshold(self):
        predictions = np.array([0.1, 0.2])
        class_indices = np.array([0, 1])
        timestamps = np.array([0.0, 3.0])

        filtered_preds, _, _ = second_stage_threshold_filter(
            predictions, class_indices, timestamps, threshold=0.5
        )

        assert len(filtered_preds) == 0


class TestPredictionsToDataframe:

    def test_basic(self):
        predictions = np.array([0.95, 0.80])
        class_indices = np.array([0, 1])
        timestamps = np.array([0.0, 3.0])
        classes = pd.DataFrame({
            "scientific_name": ["Parus major", "Erithacus rubecula"],
            "common_name": ["Great Tit", "Robin"],
            "noise": [False, False],
        })

        df = predictions_to_dataframe(predictions, class_indices, timestamps, classes, clip_dur=3.0)

        assert len(df) == 2
        assert df.iloc[0]["scientific_name"] == "Parus major"
        assert df.iloc[0]["start_time"] == 0.0
        assert df.iloc[0]["end_time"] == 3.0
        assert df.iloc[0]["confidence"] == 0.95

    def test_noise_excluded_by_default(self):
        predictions = np.array([0.95, 0.80])
        class_indices = np.array([0, 1])
        timestamps = np.array([0.0, 3.0])
        classes = pd.DataFrame({
            "scientific_name": ["Noise", "Parus major"],
            "common_name": ["Noise", "Great Tit"],
            "noise": [True, False],
        })

        df = predictions_to_dataframe(predictions, class_indices, timestamps, classes, clip_dur=3.0)

        assert len(df) == 1
        assert df.iloc[0]["scientific_name"] == "Parus major"

    def test_noise_included_when_requested(self):
        predictions = np.array([0.95])
        class_indices = np.array([0])
        timestamps = np.array([0.0])
        classes = pd.DataFrame({
            "scientific_name": ["Noise"],
            "common_name": ["Noise"],
            "noise": [True],
        })

        df = predictions_to_dataframe(predictions, class_indices, timestamps, classes, clip_dur=3.0, include_noise=True)

        assert len(df) == 1


class TestLogTransform:

    def test_base_10(self):
        x = np.array([1.0, 10.0, 100.0])
        result = log_transform(x, base=10, epsilon=0)

        np.testing.assert_array_almost_equal(result, [0.0, 1.0, 2.0])

    def test_base_2(self):
        x = np.array([1.0, 2.0, 4.0])
        result = log_transform(x, base=2, epsilon=0)

        np.testing.assert_array_almost_equal(result, [0.0, 1.0, 2.0])

    def test_epsilon_prevents_log_zero(self):
        x = np.array([0.0])
        result = log_transform(x, base=10, epsilon=1e-6)

        assert np.isfinite(result[0])


class TestStandardizeTransform:

    def test_output_has_zero_mean_and_unit_std(self):
        x = np.array([2.0, 4.0, 6.0, 8.0])
        result = standardize_transform(x)

        assert np.mean(result) == pytest.approx(0.0, abs=1e-10)
        assert np.std(result) == pytest.approx(1.0, abs=1e-10)


class TestCenterTransform:

    def test_center_mean(self):
        x = np.array([[1.0, 2.0], [3.0, 4.0]])
        result = center_transform(x, method="mean", axis=0)

        np.testing.assert_array_almost_equal(result, [[-1.0, -1.0], [1.0, 1.0]])

    def test_center_median(self):
        x = np.array([[1.0, 2.0], [3.0, 4.0], [30.0, 40.0]])
        result = center_transform(x, method="median", axis=0)

        np.testing.assert_array_almost_equal(result, [[-2.0, -2.0], [0.0, 0.0], [27.0, 36.0]])

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="Unknown method"):
            center_transform(np.array([1.0]), method="invalid")


class TestClipTransform:

    def test_clips_values(self):
        x = np.array([-5.0, 0.0, 5.0, 10.0])
        result = clip_transform(x, a_min=-1.0, a_max=6.0)

        np.testing.assert_array_equal(result, [-1.0, 0.0, 5.0, 6.0])
