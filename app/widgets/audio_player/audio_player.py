from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from widgets.audio_player.audio_info_bar import AudioInfoBar
from widgets.audio_player.main_audio_player import MainAudioPlayer


class AudioPlayer(QWidget):
    removeClicked = Signal()

    def __init__(self, file_name: Optional[str] = None):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setLayout(layout)

        self.top_bar = AudioInfoBar(file_name)
        self.top_bar.removeClick.connect(self.removeClicked)
        layout.addWidget(self.top_bar)

        self.main_view = MainAudioPlayer()
        layout.addWidget(self.main_view)

    def set_file_path(self, file_path: str):
        self.top_bar.set_file_name(Path(file_path).name)
        self.main_view.set_file_path(file_path)

    def clear_audio(self):
        self.top_bar.set_file_name(None)
        self.main_view.clear_audio()
