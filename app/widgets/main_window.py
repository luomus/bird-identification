from typing import Tuple, Union, Optional, Any
import numpy as np
import pandas as pd

from PySide6.QtCore import Qt, QSize, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QSizePolicy, QLabel
from PySide6.QtGui import QPalette, QColor, QFont

from utils.analyze import analyze_single_file, analyze_multiple_files
from utils.worker import Worker
from utils.utils import show_alert
from widgets.common.datatable import Datatable
from widgets.common.tab_widget import TabWidget
from widgets.detector_settings import DetectorSettings
from widgets.multiple_file_tab import MultipleFileTab
from widgets.single_file_tab import SingleFileTab


class MainWindow(QMainWindow):
    audio_data: Optional[Tuple[np.ndarray, Union[int, float]]] = None
    input_folder_path: Optional[str] = None
    output_folder_path: Optional[str] = None

    threshold: float = 0.6
    overlap: float = 0.5

    result_table: Optional[Datatable] = None
    single_file_result: Optional[pd.DataFrame] = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bird Identifier")

        widget = QWidget()
        self.setCentralWidget(widget)

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

        self.tab = TabWidget(self)
        self.tab.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.tab.currentChanged.connect(self.tab_changed)

        single_file = SingleFileTab()
        single_file.audioDataChanged.connect(self.audio_data_changed)
        self.tab.addTab(single_file, "Single File")

        multiple_file = MultipleFileTab()
        multiple_file.inputFolderChanged.connect(self.input_folder_changed)
        multiple_file.outputFolderChanged.connect(self.output_folder_changed)
        self.tab.addTab(multiple_file, "Multiple Files")

        self.layout.addWidget(self.tab)

        settings = DetectorSettings()
        settings.thresholdChanged.connect(self.threshold_changed)
        settings.overlapChanged.connect(self.overlap_changed)
        self.layout.addWidget(settings)

        self.analyze_button = QPushButton("Analyze")
        self.update_analyze_button_palette()
        font = self.analyze_button.font()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Medium)
        self.analyze_button.setFont(font)
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.clicked.connect(self.analyze_clicked)
        self.layout.addWidget(self.analyze_button)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.layout.addWidget(self.progress_label)

        self.result_table = Datatable()
        self.result_table.setMinimumHeight(150)
        self.result_table.setVisible(False)
        self.layout.addWidget(self.result_table, stretch=1)

        self.layout.addStretch()

        self.threadpool = QThreadPool()

        QApplication.instance().paletteChanged.connect(self.update_analyze_button_palette, Qt.ConnectionType.QueuedConnection)

    def audio_data_changed(self, audio_data: Optional[Tuple[np.ndarray, Union[int, float]]]):
        self.audio_data = audio_data

        self.single_file_result = None
        self.result_table.set_data(None)
        self.result_table.setVisible(False)

    def input_folder_changed(self, folder_path: Optional[str]):
        self.input_folder_path = folder_path

    def output_folder_changed(self, folder_path: Optional[str]):
        self.output_folder_path = folder_path

    def threshold_changed(self, value: float):
        self.threshold = value

    def overlap_changed(self, value: float):
        self.overlap = value

    def tab_changed(self, active_idx: int):
        if self.result_table is not None:
            if active_idx == 0 and self.single_file_result is not None:
                self.result_table.setVisible(True)
            else:
                self.result_table.setVisible(False)

    def analyze_clicked(self):
        self.single_file_result = None
        self.result_table.setVisible(False)

        if self.tab.currentIndex() == 0:
            if self.audio_data is None:
                show_alert(self, "Please select a file first")
                return

            worker = Worker(
                analyze_single_file,
                self.audio_data,
                threshold=self.threshold,
                overlap=self.overlap
            )
            worker.signals.result.connect(self.analyze_result_for_single_file)
        else:
            if self.input_folder_path is None or self.output_folder_path is None:
                show_alert(self, "Please select input and output folders first")
                return

            worker = Worker(
                analyze_multiple_files,
                self.input_folder_path,
                self.output_folder_path,
                threshold=self.threshold,
                overlap=self.overlap
            )

        worker.signals.finished.connect(self.analyze_finished)
        worker.signals.progress.connect(self.analyze_progressed)

        self.analyze_button.setDisabled(True)
        self.progress_label.setVisible(True)
        self.threadpool.start(worker)

    def analyze_result_for_single_file(self, result: pd.DataFrame):
        self.single_file_result = result
        self.result_table.set_data(result)

        if self.tab.currentIndex() == 0:
            self.result_table.setVisible(True)

    def analyze_finished(self):
        self.analyze_button.setDisabled(False)
        self.progress_label.setVisible(False)

    def analyze_progressed(self, data: dict[str, Any]):
        if "file" in data:
            progress_text = "Processing file {}/{}".format(data["file"], data["total_files"])
            if "chunk" in data:
                progress_text += ", chunk {}/{}".format(data["chunk"], data["total_chunks"])
        else:
            progress_text = "Processing chunk {}/{}".format(data["chunk"], data["total_chunks"])

        self.progress_label.setText(progress_text)

    def update_analyze_button_palette(self):
        palette = self.analyze_button.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("#0f598a"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, palette.window().color())
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#73828c"))
        self.analyze_button.setPalette(palette)

    def sizeHint(self) -> QSize:
        return QSize(800, 300)
