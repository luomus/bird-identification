import pandas as pd
import numpy as np
from shared import functions

def process_audio_segment(
    segment_path: str,
    classifier,
    calibration_params: np.ndarray,
    threshold: float,
    include_sdm: bool,
    include_noise: bool,
    migration_params: np.ndarray,
    lat: float,
    lon: float,
    day_of_year: int,
    species_name_list: pd.DataFrame,
    start_time: float,
    overlap: float
) -> pd.DataFrame:
    """Process an audio segment and return predictions as a DataFrame.

    Args:
        segment_path: Path to audio segment file
        classifier: Audio classifier instance
        calibration_params: Calibration parameters
        threshold: Confidence threshold
        include_sdm: Whether to apply species distribution model
        include_noise: Whether to include noise detections
        migration_params: Migration parameters for SDM
        lat: Latitude
        lon: Longitude
        day_of_year: Day of year
        species_name_list: DataFrame with species names
        start_time: Start time of segment in original file

    Returns:
        DataFrame with columns: start_time, end_time, scientific_name, common_name, confidence
    """
    # Get predictions from classifier
    species_predictions, detection_timestamps = classifier.classify(segment_path, overlap=overlap, max_pred=False)

    if len(species_predictions) == 0:
        return pd.DataFrame()

    # Convert to numpy arrays
    species_predictions = np.array(species_predictions)
    detection_timestamps = np.array(detection_timestamps)

    # Adjust timestamps relative to original file
    detection_timestamps += start_time

    # Calibrate predictions
    if calibration_params is not None:
        for i in range(len(species_predictions)):
            species_predictions[i, :] = functions.calibrate(
                species_predictions[i, :],
                calibration_params
            )
    
    # Apply threshold filter
    species_predictions, species_class_indices, detection_timestamps = functions.threshold_filter(
        species_predictions,
        detection_timestamps,
        threshold
    )

    # Apply species distribution model adjustment
    if include_sdm and len(species_predictions) > 0:
        species_predictions = functions.adjust(
            species_predictions,
            species_class_indices,
            migration_params,
            lat,
            lon,
            day_of_year
        )

        # Apply threshold filter after adjustments to discard new values below threshold
        species_predictions, species_class_indices, detection_timestamps = functions.second_stage_threshold_filter(
            species_predictions,
            species_class_indices,
            detection_timestamps,
            threshold
        )

    # Build DataFrame with results
    return functions.predictions_to_dataframe(
        species_predictions,
        species_class_indices,
        detection_timestamps,
        species_name_list,
        classifier.config.clip_duration,
        include_noise
    )

