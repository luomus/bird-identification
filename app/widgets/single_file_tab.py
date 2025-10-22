from PySide6.QtCore import Signal, QThreadPool
from PySide6.QtWidgets import QWidget, QVBoxLayout
from typing import Tuple, Union
import numpy as np
from pathlib import Path

from utils.worker import Worker
from utils.analyze import load_audio
from widgets.common.audio_drag_and_drop import AudioDragAndDrop
from widgets.audio_player.audio_player import AudioPlayer


class SingleFileTab(QWidget):
    audioDataChanged = Signal(object)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.drag_and_drop = AudioDragAndDrop()
        self.drag_and_drop.selectedFilePath.connect(self.file_selected)
        self.layout.addWidget(self.drag_and_drop)

        self.audio_player = AudioPlayer()
        self.audio_player.removeClicked.connect(self.file_removed)
        self.audio_player.setVisible(False)
        self.layout.addWidget(self.audio_player)

        self.threadpool = QThreadPool()

    def file_selected(self, file_path):
        self.audio_player.set_file_name(Path(file_path).name)

        self.drag_and_drop.setVisible(False)
        self.audio_player.setVisible(True)
        self.audio_player.set_loading(True)

        worker = Worker(load_audio, file_path)
        worker.signals.result.connect(self.audio_loaded)

        self.threadpool.start(worker)

    def file_removed(self):
        self.drag_and_drop.setVisible(True)
        self.audio_player.setVisible(False)

        self.audio_player.set_file_name(None)
        self.audio_player.set_audio_data(None, None)
        self.audioDataChanged.emit(None)

    def audio_loaded(self, data: Tuple[np.ndarray, Union[int, float]]):
        self.audio_player.set_audio_data(data[0], data[1])
        self.audio_player.set_loading(False)
        self.audioDataChanged.emit(data)
