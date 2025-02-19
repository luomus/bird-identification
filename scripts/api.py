"""An HTTP API for bird audio classification tasks

Example call:

curl -X POST "http://localhost:8000/classify?latitude=60.1699&longitude=24.9384&threshold=0.5&day_of_year=25" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@input/suomenoja/Suomenoja_20240517_000000.flac"

Examine:
docker logs bird-identification --follow

"""


import logging
from fastapi import FastAPI, File, UploadFile, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import tempfile
import os
from classifier import Classifier  # Import the Classifier class directly
from run_model import process_audio_segment
from pydantic_parameters import Metadata, AnalysisParameters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize classifier with same parameters as run_model.py
MODEL_PATH = "../models/model_v3_5.keras"
TFLITE_THREADS = 1
CLIP_DURATION = 3.0
audio_classifier = Classifier(
    path_to_mlk_model=MODEL_PATH,
    sr=48000,
    clip_dur=CLIP_DURATION,
    TFLITE_THREADS=TFLITE_THREADS,
    offset=0,
    dur=0
)

def get_current_day_of_year() -> int:
    return datetime.now().timetuple().tm_yday

class ClassificationResult(BaseModel):
    """Structure of a single element of /classify end point result"""
    start_time: float
    end_time: float
    scientific_name: str
    common_name: str
    confidence: float

@app.post("/classify", response_model=List[ClassificationResult])
async def classify_audio_file(
    latitude: float,
    longitude: float,
    threshold: Optional[float] = None,
    include_sdm: Optional[bool] = None,
    include_noise: Optional[bool] = None,
    day_of_year: Optional[int] = None,
    chunk_size: Optional[int] = None,
    file: UploadFile = File(...)
):
    
    # If day_of_year is not provided, use the current day of year. This default is set here, because it is only used in the API.
    if day_of_year is None:
        day_of_year = get_current_day_of_year()

    # Create metadata object for validation
    metadata = Metadata(
        lat=latitude,
        lon=longitude,
        day_of_year=day_of_year
    )
    
    # Create analysis parameters object
    params = AnalysisParameters(
        directory=".",  # Not used but required by the base class
        metadata=metadata,
        threshold=threshold,
        sdm=include_sdm,
        noise=include_noise
    )
    
    logger.info("Received classification request with params: %s", params.to_dict())

    # Load audio file
    logger.info("Loading audio file with sample rate 16000")
    audio_data, sr = librosa.load(file.file, sr=16000)
    logger.debug("Loaded audio data with shape: %s", audio_data.shape)
    all_results = pd.DataFrame()
    
    # Load required data
    logger.info("Loading calibration and migration parameters")
    calibration_params = np.load("Pred_adjustment/calibration_params.npy")
    migration_params = np.load("Pred_adjustment/migration_params.npy")
    species_name_list = pd.read_csv("classes.csv")
    logger.debug("Loaded species list with %d entries", len(species_name_list))
    
    # Create temporary directory for chunks
    logger.info("Creating temporary directory for audio chunks")
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.debug("Created temp directory at: %s", temp_dir)
        # Process in chunks
        chunk_size = chunk_size * sr
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            if len(chunk) == 0:
                continue
                
            # Create temporary file for chunk
            temp_file_path = os.path.join(temp_dir, f"chunk_{i}.wav")
            logger.debug("Writing chunk %d to %s", i, temp_file_path)
            sf.write(temp_file_path, chunk, sr)
            
            # Process audio segment using run_model's function
            logger.info("Processing audio chunk %d (%.2f-%.2f seconds)", 
                       i, i/sr, (i+chunk_size)/sr)
            results_df = process_audio_segment(
                temp_file_path,
                audio_classifier,
                calibration_params,
                params.threshold,
                params.sdm,
                params.noise,
                migration_params,
                params.lat,
                params.lon,
                params.day_of_year,
                species_name_list,
                i / sr  # start_time
            )
            
            if not results_df.empty:
                logger.debug("Chunk %d results: %d detections", 
                           i, len(results_df))
                all_results = pd.concat([all_results, results_df])
            else:
                logger.debug("No detections in chunk %d", i)
    
    logger.info("Completed processing with %d total detections", len(all_results))
    return all_results.to_dict('records')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
