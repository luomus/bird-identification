from math import floor
import librosa
from typing import Optional, Tuple
from threading import Event
from numpy import interp

import numpy as np
from PySide6 import QtGui
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QPen

from functions.exceptions import CancelRequested
from functions.worker import Worker
from widgets.common.spinner import WaitingSpinner


def _calculate_peaks(file_path: str, width: int, height: int, cancel_requested: Event, target_chunk_sec = 600) -> Tuple[np.ndarray, float, float]:
    peak_table = np.ndarray((width, 2), dtype=np.float32)

    duration = librosa.get_duration(path=file_path)
    sr = librosa.get_samplerate(file_path)

    if duration == 0 or sr == 0:
        raise ValueError("Failed to load audio")

    samples_per_pixel = max(round(sr * duration / width), 1)

    target_samples_per_chunk = target_chunk_sec * sr
    pixels_per_chunk = max(round(target_samples_per_chunk / samples_per_pixel), 1)
    samples_per_chunk = pixels_per_chunk * samples_per_pixel
    chunk_sec = samples_per_chunk / sr

    max_abs_value = 0.0

    pixel = 0
    offset = 0.0

    while offset < duration and pixel < width:
        if cancel_requested.is_set():
            raise CancelRequested()

        y, _ = librosa.load(
            file_path,
            sr=sr,
            mono=True,
            offset=offset,
            duration=chunk_sec
        )

        start = 0

        while start < len(y) and pixel < width:
            end = start + samples_per_pixel
            values = y[start:end]

            if values.size == 0:
                break

            min_value = values.min()
            max_value = values.max()

            peak_table[pixel] = [min_value, max_value]

            max_abs_value = max(max_abs_value, abs(max_value), abs(min_value))

            start = end
            pixel += 1

        offset += chunk_sec

    peak_table[:, 0] = interp(peak_table[:, 0], [-max_abs_value, max_abs_value], [0, height - 1])
    peak_table[:, 1] = interp(peak_table[:, 1], [-max_abs_value, max_abs_value], [0, height - 1])

    return peak_table, duration, sr

def _resample_peaks_for_width(peaks: np.ndarray, width: int):
    result = np.ndarray((width, 2), dtype=np.float32)

    step = len(peaks) / width

    for x in range(width):
        i1 = int(x * step)
        i2 = int((x + 1) * step)
        segment = peaks[i1:i2]
        result[x, 0] = segment[:, 0].min()
        result[x, 1] = segment[:, 1].max()

    return result

def _play_time_as_pixel(time: int, duration: float, sample_rate: float, width: int):
    samples = round(time * sample_rate / 1000)
    total_samples = int(duration * sample_rate)
    pixel = round(samples * width / total_samples)
    return pixel

def _pixel_as_play_time(pixel: int, duration: float, sample_rate: float, width: int):
    total_samples = int(duration * sample_rate)
    samples = (pixel * total_samples) / width
    time = round(samples / sample_rate * 1000)
    return time

class WaveformView(QWidget):
    waveformReady = Signal(float)
    timeClicked = Signal(int)

    default_pen = QtGui.QPen(QtGui.QColor("#777"))
    active_pen = QPen(QColor(15, 89, 138))

    file_path: Optional[str] = None

    lines = []

    peaks: np.ndarray = np.array([])
    duration = 0
    sample_rate = 0

    play_time = 0

    worker: Optional[Worker] = None

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedHeight(50)
        self.view.setStyleSheet("background: transparent; border: none")
        layout.addWidget(self.view)

        self.loading_spinner = WaitingSpinner(self)
        self.loading_spinner.hide()
        layout.addWidget(self.loading_spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        self.error_label = QLabel("Failed to load audio")
        self.error_label.hide()
        layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.threadpool = QThreadPool()

    def set_file_path(self, file_path: str):
        self.clear_audio()
        self.file_path = file_path
        self.calculate_peaks()

    def clear_audio(self):
        if self.worker:
            self.worker.cancel()

        self.file_path = None
        self.lines = []
        self.peaks = np.array([])
        self.duration = 0
        self.sample_rate = 0
        self.play_time = 0

        self.error_label.hide()
        self.set_loading(False)

    def set_play_time(self, time):
        self.play_time = time

        if len(self.lines) == 0:
            return

        pixel = _play_time_as_pixel(time, self.duration, self.sample_rate, len(self.lines))

        for i, line in enumerate(self.lines):
            if i <= pixel:
                line.setPen(self.active_pen)
            else:
                line.setPen(self.default_pen)

    def resizeEvent(self, event: QtGui.QMouseEvent):
        self.draw()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if len(self.lines) == 0:
            return

        pixel = int(self.view.mapToScene(event.pos()).x())
        time = _pixel_as_play_time(pixel, self.duration, self.sample_rate, len(self.lines))

        self.timeClicked.emit(time)

    def calculate_peaks(self):
        if self.file_path is None:
            return

        self.worker = Worker(_calculate_peaks, self.file_path, 200000, int(self.view.height()))
        self.worker.signals.result.connect(self.on_peaks_calculated)
        self.worker.signals.error.connect(self.on_error)

        self.set_loading(True)
        self.threadpool.start(self.worker)

    def on_peaks_calculated(self, result: Tuple[np.ndarray, float, float, int]):
        if self.worker.is_canceled():
            return

        self.set_loading(False)

        peaks, duration, sr = result

        self.peaks = peaks
        self.duration = duration
        self.sample_rate = sr

        self.draw()

        self.waveformReady.emit(duration)

    def on_error(self):
        if self.worker.is_canceled():
            return

        self.set_loading(False)
        self.view.hide()
        self.error_label.show()

    def set_loading(self, loading: bool):
        if loading:
            self.loading_spinner.start()
            self.view.hide()
            self.loading_spinner.show()
        else:
            self.loading_spinner.stop()
            self.loading_spinner.hide()
            self.view.show()

    def draw(self):
        self.scene.clear()

        width = self.view.width()
        height = self.view.height()
        self.scene.setSceneRect(0, 0, width, height)

        if len(self.peaks) == 0:
            return

        self.lines = []

        peaks = _resample_peaks_for_width(self.peaks, width)
        pixel = _play_time_as_pixel(self.play_time, self.duration, self.sample_rate, width)

        for i, peak in enumerate(peaks):
            line = QGraphicsLineItem(i, peak[0], i, peak[1])
            if i <= pixel:
                line.setPen(self.active_pen)
            else:
                line.setPen(self.default_pen)

            self.lines.append(line)
            self.scene.addItem(line)

        self.view.fitInView(self.scene.sceneRect())
