import tensorflow
from tensorflow import keras
import numpy as np
import librosa
import os
from functions import pad, split_signal
import time

# Classifier

class Classifier():
    def __init__(self, path_to_mlk_model='', sr=48000, clip_dur=3.0, TFLITE_THREADS = 1, offset=0, dur=0):
        self.sr = sr
        self.clip_dur = 3.0
        self.dur=dur
        self.offset=offset
        self.MLK_MODEL_PATH = path_to_mlk_model
        self.BIRDNED_MODEL_PATH: str = '../models/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite'
        self.TFLITE_THREADS = TFLITE_THREADS # can be as high as number of CPUs
        ######################################
        # Initialize BirdNET feature extractor
        ######################################
        try:
            import tflite_runtime.interpreter as tflite
        except ModuleNotFoundError:
            from tensorflow import lite as tflite
        self.INTERPRETER = tflite.Interpreter(model_path=self.BIRDNED_MODEL_PATH, num_threads=self.TFLITE_THREADS)
        self.INTERPRETER.allocate_tensors()
        # Get input and output tensors.
        input_details = self.INTERPRETER.get_input_details()
        output_details = self.INTERPRETER.get_output_details()
        # Get input tensor index
        self.INPUT_LAYER_INDEX = input_details[0]["index"]
        # Get classification output or feature embeddings
        self.OUTPUT_LAYER_INDEX = output_details[0]["index"] - 1
        ################################
        # Initialize classification head
        ################################
        self.model = keras.models.load_model(self.MLK_MODEL_PATH)

    def embeddings(self, sample):
        # Reshape input tensor
        self.INTERPRETER.resize_tensor_input(self.INPUT_LAYER_INDEX, [len(sample), *sample[0].shape])
        self.INTERPRETER.allocate_tensors()
        # Extract feature embeddings
        self.INTERPRETER.set_tensor(self.INPUT_LAYER_INDEX, np.array(sample, dtype="float32"))
        self.INTERPRETER.invoke()
        features = self.INTERPRETER.get_tensor(self.OUTPUT_LAYER_INDEX)
        return features
    
    def classify(self, data_path, overlap=1.0, max_pred=True):
        # Start timing
        start = time.time()

        print(f"Using overlap: {overlap}")

        print(f"Loading file {data_path}")
        if self.dur>0:
                sig, sr = librosa.load(data_path, sr=self.sr, mono=True, res_type='kaiser_fast', offset=self.offset, duration=self.dur)
        else:
            sig, sr = librosa.load(data_path, sr=self.sr, mono=True, res_type='kaiser_fast')
        chunks = split_signal(sig, self.sr, self.clip_dur, overlap)
        samples = []
        for c in range(len(chunks)):
            samples.append(chunks[c])
        X = np.array(samples, dtype='float32')
        print(f"Classifying segment")
        X = self.model(self.embeddings(X))
        X = X.numpy()
        print("Segment classification done")

        # End timing
        end = time.time()
        print(f"Classification took {round(end - start, 1)} seconds")

        if max_pred: # return maximum prediction for each species
            pred = list(map(max, zip(*X))) # return max predictions for each class
            t = np.argmax(X, 0)*(self.clip_dur-overlap) # return timepoints of max prediction
        else:
            pred = X
            t = np.array(range(len(X)))*(self.clip_dur-overlap)
        return pred, t
