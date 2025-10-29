from typing import Optional, Union
import numpy as np

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from widgets.audio_player.audio_info_bar import AudioInfoBar
from widgets.audio_player.main_audio_player import MainAudioPlayer


class AudioPlayer(QWidget):
    removeClicked = Signal()

    def __init__(self, file_name: Optional[str] = None):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.top_bar = AudioInfoBar(file_name)
        self.top_bar.removeClick.connect(self.removeClicked)
        layout.addWidget(self.top_bar)

        self.main_view = MainAudioPlayer()
        layout.addWidget(self.main_view)

    def set_loading(self, loading: bool):
        self.main_view.set_loading(loading)

    def set_file_name(self, file_name: Optional[str]):
        self.top_bar.set_file_name(file_name)

    def set_audio_data(self, file_path: str, audio_data: np.ndarray, sample_rate: Union[int, float]):
        self.main_view.set_audio_data(file_path, audio_data, sample_rate)

    def clear_audio(self):
        self.main_view.clear_audio()
3