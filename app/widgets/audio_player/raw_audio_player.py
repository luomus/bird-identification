import numpy as np
from typing import Optional, Union

from PySide6.QtCore import Signal, QBuffer, QByteArray, QIODevice, QTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtMultimedia import QAudioFormat, QMediaDevices, QAudioSink, QAudio, QAudioDevice


def float_to_pcm(data: np.ndarray, dtype="int16") -> np.ndarray:
    dtype = np.dtype(dtype)
    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (data * abs_max + offset).clip(i.min, i.max).astype(dtype)


class RawAudioPlayer(QWidget):
    playingChanged = Signal(bool)
    playTimeChanged = Signal(int)

    def __init__(self):
        super().__init__()

        device_info = QMediaDevices.defaultAudioOutput()

        audio_format = QAudioFormat()
        audio_format.setSampleRate(44100)
        audio_format.setChannelCount(1)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        self.byte_array = QByteArray()
        self.buffer = QBuffer()

        self.sink = QAudioSink(device_info, audio_format)
        self.sink.stateChanged.connect(self.state_changed)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_played_time)

    def set_audio(self, audio_data: Optional[np.ndarray], sample_rate: Optional[Union[int, float]]):
        self.sink.reset()

        if audio_data is None:
            self.byte_array = QByteArray()
        else:
            pcm_bytes = float_to_pcm(audio_data).tobytes()
            self.byte_array = QByteArray(pcm_bytes)

        self.buffer.setBuffer(self.byte_array)
        self.set_sample_rate(sample_rate)

    def start(self):
        if self.sink.processedUSecs() > 0:
            self.sink.resume()
        else:
            self.buffer.open(QIODevice.OpenModeFlag.ReadOnly)
            self.sink.start(self.buffer)

    def stop(self):
        self.sink.suspend()

    def state_changed(self):
        state = self.sink.state()

        if state == QAudio.State.IdleState:
            self.sink.reset()
        elif state == QAudio.State.StoppedState or state == QAudio.State.SuspendedState:
            if state == QAudio.State.StoppedState:
                self.buffer.close()

            self.update_played_time()
            self.timer.stop()

            self.playingChanged.emit(False)
        elif state == QAudio.State.ActiveState:
            self.timer.start(50)

            self.playingChanged.emit(True)

    def update_played_time(self):
        self.playTimeChanged.emit(self.sink.processedUSecs())

    def set_sample_rate(self, sample_rate: Optional[Union[int, float]]):
        if sample_rate is not None and self.sink.format().sampleRate != sample_rate:
            device_info = QMediaDevices.defaultAudioOutput()

            new_format = self.sink.format()
            new_format.setSampleRate(sample_rate)

            self.update_sink(device_info, new_format)

    def update_sink(self, device_info: QAudioDevice, audio_format: QAudioFormat):
        self.sink = QAudioSink(device_info, audio_format)
        self.sink.stateChanged.connect(self.state_changed)
