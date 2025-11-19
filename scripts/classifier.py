import numpy as np
import librosa
from scripts.functions import split_signal
import time

from tensorflow import lite as tflite, keras

# Classifier

class Classifier():
    def __init__(self, path_to_mlk_model='', path_to_birdnet_model='', sr=48000, clip_dur=3.0, TFLITE_THREADS = 1):
        self.sr = sr
        self.clip_dur = clip_dur
        self.MLK_MODEL_PATH = path_to_mlk_model
        self.BIRDNED_MODEL_PATH = path_to_birdnet_model
        self.TFLITE_THREADS = TFLITE_THREADS # can be as high as number of CPUs
        ######################################
        # Initialize BirdNET feature extractor
        ######################################

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
        if self.MLK_MODEL_PATH:
            self.model = keras.models.load_model(self.MLK_MODEL_PATH)
        else:
            self.model = None

    def set_model_path(self, path_to_mlk_model):
        if path_to_mlk_model != self.MLK_MODEL_PATH:
            self.MLK_MODEL_PATH = path_to_mlk_model
            self.model = keras.models.load_model(path_to_mlk_model)

    def interpret(self, sample):
        current_shape = self.INTERPRETER.get_input_details()[self.INPUT_LAYER_INDEX]["shape"]

        if list(current_shape) != list(sample.shape):
            self.INTERPRETER.resize_tensor_input(self.INPUT_LAYER_INDEX, sample.shape)
            self.INTERPRETER.allocate_tensors()

        self.INTERPRETER.set_tensor(self.INPUT_LAYER_INDEX, sample)
        self.INTERPRETER.invoke()
        return self.INTERPRETER.get_tensor(self.OUTPUT_LAYER_INDEX)

    def classify(self, data_path, overlap=1.0, max_pred=True, offset=None, duration=None):
        if self.model is None:
            raise ValueError("Model path is not set")

        # Start timing
        start = time.time()

        print(f"Using overlap: {overlap}")

        print(f"Loading file {data_path}")
        sig, sr = librosa.load(data_path, sr=self.sr, mono=True, res_type='kaiser_fast', offset=offset, duration=duration)
        samples = split_signal(sig, self.sr, self.clip_dur, overlap)
        X = np.array(samples, dtype='float32')

        print(f"Classifying segment")
        X = self.interpret(X)
        X = self.model(X)
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
