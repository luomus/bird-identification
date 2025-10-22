from typing import Optional, Union
import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QIcon

from widgets.audio_player.raw_audio_player import RawAudioPlayer
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
        layout.addWidget(self.waveform)

        time_layout = QHBoxLayout()
        layout.addLayout(time_layout)

        start_time_label = QLabel("00:00:00")
        time_layout.addWidget(start_time_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.end_time_label = QLabel("00:00:00")
        time_layout.addWidget(self.end_time_label, 0, Qt.AlignmentFlag.AlignRight)

        icon = QIcon(":/icons/play-solid-full.svg")
        self.play_button = IconButton(icon)
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.the_button_was_toggled)
        self.play_button.setEnabled(False)
        layout.addWidget(self.play_button)

        self.player = RawAudioPlayer()
        self.player.playingChanged.connect(self.playing_changed)
        self.player.playTimeChanged.connect(self.play_time_changed)

    def set_loading(self, loading: bool):
        self.play_button.setEnabled(not loading)
        self.waveform.set_loading(loading)

    def set_audio_data(self, audio_data: Optional[np.ndarray], sample_rate: Optional[Union[int, float]]):
        self.player.set_audio(audio_data, sample_rate)
        self.waveform.set_audio(audio_data, sample_rate)
        self.play_button.setEnabled(audio_data is not None)

        end_time = "00:00:00"

        if audio_data is not None and sample_rate is not None:
            duration = len(audio_data) / sample_rate
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            end_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

        self.end_time_label.setText(end_time)

    def the_button_was_toggled(self, checked: bool):
        if checked:
            self.player.start()
        else:
            self.player.stop()

    def playing_changed(self, playing: bool):
        if playing:
            self.play_button.setChecked(True)
        else:
            self.play_button.setChecked(False)

    def play_time_changed(self, duration: int):
        self.waveform.set_play_time(duration)
