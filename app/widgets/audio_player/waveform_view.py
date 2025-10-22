from math import floor

import numpy as np
from PySide6 import QtGui
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QVBoxLayout
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QColor, QPen

from numpy import interp

from utils.worker import Worker
from widgets.common.spinner import WaitingSpinner


def get_samples_per_pixel(audio_data: np.ndarray, width: int) -> float:
    total_samples = len(audio_data)
    return total_samples / float(width)


def calculate_lines(audio_data: np.ndarray, width: int, height: int, **kwargs) -> np.ndarray:
    lines = np.ndarray(shape=(width, 4))

    y_middle = height / 2

    samples_per_pixel = get_samples_per_pixel(audio_data, width)

    total_max = np.max(audio_data)
    total_min = np.min(audio_data)

    start = 0

    for pixel in range(width):
        end = round((pixel + 1) * samples_per_pixel)

        values = audio_data[start:end]
        min_value = np.min(values)
        max_value = np.max(values)

        start_y = min(interp(min_value, [total_min, total_max], [0, height]), y_middle)
        end_y = max(interp(max_value, [total_min, total_max], [0, height]), y_middle)

        lines[pixel] = [pixel, start_y, pixel, end_y]

        start = end

    return lines


class WaveformView(QWidget):
    default_pen = QtGui.QPen(QtGui.QColor("#777"))
    active_pen = QPen(QColor(15, 89, 138))

    audio_data = None
    sample_rate = None

    lines = []
    samples_per_pixel = 0

    def __init__(self, /):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scene = QGraphicsScene(0, 0, 700, 50)
        self.view = QGraphicsView(self.scene)
        self.view.setFixedHeight(50)
        layout.addWidget(self.view)

        self.loading_spinner = WaitingSpinner(self)
        self.loading_spinner.setVisible(False)
        layout.addWidget(self.loading_spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        self.threadpool = QThreadPool()

    def set_loading(self, loading: bool):
        if loading:
            self.loading_spinner.start()
            self.loading_spinner.setVisible(True)
            self.view.setVisible(False)
        else:
            self.loading_spinner.stop()
            self.loading_spinner.setVisible(False)
            self.view.setVisible(True)

    def resizeEvent(self, event):
        self.view.fitInView(self.scene.sceneRect())

    def draw(self):
        self.scene.clear()

        self.lines = []

        if self.audio_data is None or self.sample_rate is None:
            return

        margin_bottom = 0
        width = int(self.scene.width())
        height = int(self.scene.height()) - margin_bottom

        self.samples_per_pixel = get_samples_per_pixel(self.audio_data, width)

        worker = Worker(calculate_lines, self.audio_data, width, height)
        worker.signals.result.connect(self.lines_calculated)

        self.threadpool.start(worker)

    def lines_calculated(self, result: np.ndarray):
        for line_data in result:
            line = QGraphicsLineItem(*line_data)
            line.setPen(self.default_pen)

            self.lines.append(line)
            self.scene.addItem(line)

            self.view.fitInView(self.scene.sceneRect())

    def set_audio(self, audio_data, sample_rate):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.draw()

    def set_play_time(self, time):
        if len(self.lines) == 0:
            return

        nbr_of_samples = round(time * self.sample_rate / 1000)
        nbr_of_pixels = floor(nbr_of_samples / self.samples_per_pixel)

        for i, line in enumerate(self.lines):
            if i < nbr_of_pixels:
                line.setPen(self.active_pen)
            else:
                line.setPen(self.default_pen)
