from typing import Union
import numpy as np

from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QPalette

from widgets.audio_player.waveform_view import WaveformView
from widgets.common.icon_button import IconButton


class MainAudioPlayer(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.waveform = WaveformView()
        self.waveform.setFixedHeight(50)
        self.waveform.timeClicked.connect(self.on_time_click)
        layout.addWidget(self.waveform)

        time_layout = QHBoxLayout()
        layout.addLayout(time_layout)

        start_time_label = QLabel("00:00:00")
        palette = self.waveform.palette()
        muted = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text)
        palette.setColor(QPalette.ColorRole.WindowText, muted)
        start_time_label.setPalette(palette)
        font = self.waveform.font()
        font.setPointSize(8)
        start_time_label.setFont(font)
        time_layout.addWidget(start_time_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.end_time_label = QLabel("00:00:00")
        self.end_time_label.setPalette(palette)
        self.end_time_label.setFont(font)
        time_layout.addWidget(self.end_time_label, 0, Qt.AlignmentFlag.AlignRight)

        self.play_button = IconButton()
        self.on_playing_changed(False)
        self.play_button.clicked.connect(self.on_play_button_click)
        self.play_button.setEnabled(False)
        layout.addWidget(self.play_button)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.playingChanged.connect(self.on_playing_changed)
        self.player.positionChanged.connect(self.on_play_time_changed)

    def set_loading(self, loading: bool):
        self.play_button.setEnabled(not loading)
        self.waveform.set_loading(loading)

    def set_audio_data(self, file_path: str, audio_data: np.ndarray, sample_rate: Union[int, float]):
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.waveform.set_audio(audio_data, sample_rate)
        self.play_button.setEnabled(True)

        duration = len(audio_data) / sample_rate
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        end_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        self.end_time_label.setText(end_time)

    def clear_audio(self):
        self.waveform.set_audio(None, None)
        self.play_button.setEnabled(False)
        self.end_time_label.setText("00:00:00")

    def on_play_button_click(self):
        if self.player.isPlaying():
            self.player.pause()
        else:
            self.player.play()

    def on_playing_changed(self, playing: bool):
        if playing:
            self.play_button.set_icon(":/icons/pause-solid-full.svg", ":/icons/pause-solid-full-dark.svg")
        else:
            self.play_button.set_icon(":/icons/play-solid-full.svg", ":/icons/play-solid-full-dark.svg")

    def on_play_time_changed(self, duration: int):
        self.waveform.set_play_time(duration)

    def on_time_click(self, time: int):
        self.player.setPosition(time)
        self.player.play()
