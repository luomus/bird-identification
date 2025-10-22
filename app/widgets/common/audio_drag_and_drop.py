from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QFileDialog

from utils.utils import is_audio_file


class AudioDragAndDrop(QFrame):

    selectedFilePath = Signal(str)

    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        audio_icon = QIcon(":/icons/headphones-solid-full.svg")
        audio_icon_label = QLabel()
        audio_icon_label.setPixmap(audio_icon.pixmap(QSize(46, 46)))
        audio_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(audio_icon_label)

        label = QLabel("Click to select a file or drag it here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.dialog = QFileDialog()
        self.dialog.setWindowTitle("Select a file")
        self.dialog.setNameFilter("Audio (*.mp3 *.MP3 *.wav *.WAV *.flac *.FLAC)")
        self.dialog.finished.connect(self.on_finished)

    def on_finished(self):
        if len(self.dialog.selectedFiles()) > 0:
            file_path = self.dialog.selectedFiles()[0]
            if is_audio_file(file_path):
                self.selectedFilePath.emit(file_path)

    def mousePressEvent(self, e):
        self.dialog.open()

    # Methods for dragging and dropping
    def dragEnterEvent(self, e):
        if self._get_audio_file_path(e):
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._get_audio_file_path(e):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        file_path = self._get_audio_file_path(e)

        if file_path:
            e.setDropAction(Qt.DropAction.CopyAction)
            e.accept()

            self.selectedFilePath.emit(file_path)
        else:
            e.ignore()

    def _get_audio_file_path(self, e):
        urls = e.mimeData().urls()

        if urls and urls[0].scheme() == "file":
            file_path = urls[0].toLocalFile()

            if is_audio_file(file_path):
                return file_path
