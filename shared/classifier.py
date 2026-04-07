from typing import Union, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
import librosa

from shared.classifier_config import ClassifierConfig, ResultFormat, LogPreprocessing, StandardizePreprocessing, \
    CenterPreprocessing, ClipPreprocessing
from shared.functions import split_signal, wav_to_spectrogram_chunks,log_transform, \
    standardize_transform, center_transform, clip_transform
import time

from tensorflow import lite as tflite, keras
from tensorflow.nn import softmax

# Classifier

class Classifier:
    config = ClassifierConfig()
    keras_model = None
    tflite_interpreter = None
    birdnet_interpreter = None

    def __init__(self, config: ClassifierConfig):
        self.set_config(config)

    def set_config(self, config: ClassifierConfig):
        if config.model_path != self.config.model_path:
            self.keras_model = None
            self.tflite_interpreter = None

            if config.model_path:
                if not config.model_path.endswith('.tflite'):
                    self.keras_model = keras.models.load_model(config.model_path)
                else:
                    self.tflite_interpreter = tflite.Interpreter(model_path=config.model_path, num_threads=config.tflite_threads)
                    self.tflite_interpreter.allocate_tensors()

        if config.raw_config.birdnet_model_path != self.config.raw_config.birdnet_model_path:
            if config.raw_config.birdnet_model_path:
                self.birdnet_interpreter = tflite.Interpreter(model_path=config.raw_config.birdnet_model_path, num_threads=config.tflite_threads)
                self.birdnet_interpreter.allocate_tensors()
            else:
                self.birdnet_interpreter = None

        self.config = config

    def classify(self, data_path: str, overlap: Union[int, float] = 1.0, max_pred: bool = True, offset: float = 0.0, duration: Optional[float] = None) -> Tuple[NDArray, NDArray]:
        if self.config.model_path is None:
            raise RuntimeError("Model path is not set")

        start = time.time()
        print(f"Using overlap: {overlap}")

        print(f"Loading file {data_path}")
        sig, sr = librosa.load(data_path, sr=self.config.sample_rate, mono=True, res_type='kaiser_fast', offset=offset, duration=duration)

        print("Classifying segment")
        if not self.config.requires_spectrogram:
            pred, t = self._classify_raw_waveform(sig, overlap, max_pred)
        else:
            pred, t = self._classify_spectrogram(sig, overlap, max_pred)

        if self.config.result_format == ResultFormat.LOGITS:
            pred = softmax(pred, axis=-1).numpy()

        print("Segment classification done")
        end = time.time()
        print(f"Classification took {round(end - start, 1)} seconds")

        return pred, t

    def _classify_raw_waveform(self, sig: NDArray, overlap: Union[int, float], max_pred: bool) -> Tuple[NDArray, NDArray]:
        samples = split_signal(sig, self.config.sample_rate, self.config.raw_config.clip_duration, overlap)
        x = np.array(samples, dtype='float32')
        x = self._apply_preprocessing(x)

        if self.config.raw_config.requires_birdnet:
            x = self._interpret(x, self.birdnet_interpreter, -1)

        y = self._run_model(x)

        if max_pred: # return maximum prediction for each species
            pred = list(map(max, zip(*y))) # return max predictions for each class
            t = np.argmax(y, axis=0) * (self.config.raw_config.clip_duration - overlap) # return timepoints of max prediction
        else:
            pred = y
            t = np.arange(len(y)) * (self.config.raw_config.clip_duration - overlap)

        return pred, t

    def _classify_spectrogram(self, sig: NDArray, overlap: Union[int, float], max_pred: bool) -> Tuple[NDArray, NDArray]:
        s_config = self.config.spectrogram_config
        overlap_frames = round(overlap * self.config.sample_rate / s_config.hop_length)

        spectrograms = wav_to_spectrogram_chunks(
            sig,
            self.config.sample_rate,
            s_config.input_height,
            s_config.input_width,
            overlap_frames,
            s_config.n_fft,
            s_config.hop_length,
            s_config.n_mels,
            s_config.fmin,
            s_config.fmax
        )
        spectrograms = self._apply_preprocessing(spectrograms)

        if s_config.channels_first:
            x = spectrograms[:, np.newaxis, :, :]
        else:
            x = spectrograms[:, :, :, np.newaxis]

        y = self._run_model(x)
        spec_step = overlap_frames * (s_config.hop_length / self.config.sample_rate)

        if max_pred:
            pred = list(map(max, zip(*y)))
            t = np.argmax(y, axis=0) * spec_step
        else:
            pred = y
            t = np.arange(len(y)) * spec_step

        return pred, t

    def _apply_preprocessing(self, chunks: NDArray) -> NDArray:
        for i in range(len(chunks)):
            for step in self.config.preprocessing:
                if isinstance(step, LogPreprocessing):
                    chunks[i] = log_transform(chunks[i], step.base, step.epsilon)
                elif isinstance(step, StandardizePreprocessing):
                    chunks[i] = standardize_transform(chunks[i])
                elif isinstance(step, CenterPreprocessing):
                    chunks[i] = center_transform(chunks[i], method=step.method, axis=step.axis)
                elif isinstance(step, ClipPreprocessing):
                    chunks[i] = clip_transform(chunks[i], step.range[0], step.range[1])
                else:
                    raise TypeError(f"Unknown preprocessing step: {type(step)}")

        return chunks

    def _run_model(self, x: NDArray) -> NDArray:
        input_shape_signature = self.keras_model.input_shape if self.keras_model else self.tflite_interpreter.get_input_details()[0]["shape_signature"]
        output_shape = self.keras_model.output_shape if self.keras_model else self.tflite_interpreter.get_output_details()[0]["shape"]

        batch_size = input_shape_signature[0] if input_shape_signature[0] is not None else len(x)
        n = len(x)
        result = np.zeros((n, output_shape[1]))

        for i in range(0, n, batch_size):
            batch = x[i:i + batch_size]
            # Pad last batch if needed
            if len(batch) < batch_size:
                pad = batch_size - len(batch)
                pad_width = np.array([[0, pad]] + [[0, 0]] * (batch.ndim - 1), dtype=int)
                batch = np.pad(
                    batch,
                    pad_width,
                    mode="constant"
                )

            if self.keras_model is not None:
                y = self.keras_model(batch).numpy()
            else:
                y = self._interpret(batch, self.tflite_interpreter)

            result[i:i + batch_size] = y[:min(batch_size, n - i)]

        return result

    def _interpret(self, sample: NDArray, interpreter: tflite.Interpreter, output_layer_offset: int = 0) -> NDArray:
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        input_layer_index = input_details[0]['index']
        output_layer_index = output_details[0]['index'] + output_layer_offset

        current_shape = input_details[input_layer_index]["shape"]

        if list(current_shape) != list(sample.shape):
            interpreter.resize_tensor_input(input_layer_index, sample.shape)
            interpreter.allocate_tensors()

        interpreter.set_tensor(input_layer_index, sample)
        interpreter.invoke()
        return interpreter.get_tensor(output_layer_index)
