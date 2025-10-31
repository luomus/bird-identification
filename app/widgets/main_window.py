from typing import Tuple, Union, Optional, Any
import numpy as np
import pandas as pd

from PySide6.QtCore import Qt, QSize, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QSizePolicy, QLabel, \
    QHBoxLayout
from PySide6.QtGui import QPalette, QColor, QFont

from utils.analyze import analyze_single_file, analyze_multiple_files
from utils.worker import Worker
from utils.utils import show_alert
from widgets.common.datatable import Datatable
from widgets.common.spinner import WaitingSpinner
from widgets.common.tab_widget import TabWidget
from widgets.detector_settings import DetectorSettings
from widgets.multiple_file_tab import MultipleFileTab
from widgets.single_file_tab import SingleFileTab


class MainWindow(QMainWindow):
    single_file_path: Optional[str] = None
    single_file_audio_data: Optional[Tuple[np.ndarray, Union[int, float]]] = None
    single_file_analyze_started: bool = False
    single_file_results: Optional[pd.DataFrame] = None

    multiple_files_input_folder_path: Optional[str] = None
    multiple_files_output_folder_path: Optional[str] = None

    threshold: float = 0.6
    overlap: float = 0.5

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bird Identifier")

        widget = QWidget()
        self.setCentralWidget(widget)

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

        self.tabs = TabWidget(self)
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.single_file_tab = SingleFileTab()
        self.single_file_tab.fileSelected.connect(self.on_single_file_select)
        self.single_file_tab.audioDataLoaded.connect(self.on_audio_load)
        self.tabs.addTab(self.single_file_tab, "Single File")

        multiple_file_tab = MultipleFileTab()
        multiple_file_tab.inputFolderChanged.connect(self.on_input_folder_change)
        multiple_file_tab.outputFolderChanged.connect(self.on_output_folder_change)
        self.tabs.addTab(multiple_file_tab, "Multiple Files")

        self.tabs.currentChanged.connect(self.on_tab_change)
        self.layout.addWidget(self.tabs)

        settings = DetectorSettings()
        settings.thresholdChanged.connect(self.on_threshold_change)
        settings.overlapChanged.connect(self.on_overlap_change)
        self.layout.addWidget(settings)

        self.analyze_button = QPushButton("Analyze")
        self._update_analyze_button_palette()
        font = self.analyze_button.font()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Medium)
        self.analyze_button.setFont(font)
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.clicked.connect(self.on_analyze_click)
        self.layout.addWidget(self.analyze_button)

        progress_layout = QHBoxLayout()
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(progress_layout)

        self.progress_spinner = WaitingSpinner(self, False, lines=10, line_length=5, radius=5)
        progress_layout.addWidget(self.progress_spinner)
        self.progress_label = QLabel("")
        progress_layout.addWidget(self.progress_label)
        self.multiple_files_analyze_result_label = QLabel("")
        self.multiple_files_analyze_result_label.setVisible(False)
        progress_layout.addWidget(self.multiple_files_analyze_result_label)

        self.single_file_result_table = Datatable()
        self.single_file_result_table.setMinimumHeight(150)
        self.single_file_result_table.setVisible(False)
        self.layout.addWidget(self.single_file_result_table, stretch=1)

        self.layout.addStretch()

        self.threadpool = QThreadPool()

        QApplication.instance().paletteChanged.connect(self._update_analyze_button_palette, Qt.ConnectionType.QueuedConnection)

    def on_single_file_select(self, file_path: str):
        self.single_file_path = file_path if file_path != "" else None
        self.single_file_audio_data = None
        self._clear_single_file_results()

    def on_input_folder_change(self, folder_path: str):
        self.multiple_files_input_folder_path = folder_path

    def on_output_folder_change(self, folder_path: str):
        self.multiple_files_output_folder_path = folder_path

    def on_threshold_change(self, value: float):
        self.threshold = value

    def on_overlap_change(self, value: float):
        self.overlap = value

    def on_tab_change(self, active_idx: int):
        if active_idx == 0:
            if self.single_file_results is not None:
                self.single_file_result_table.setVisible(True)
            self.multiple_files_analyze_result_label.setVisible(False)
        else:
            self.single_file_result_table.setVisible(False)
            self.multiple_files_analyze_result_label.setVisible(True)

    def on_analyze_click(self):
        self._clear_single_file_results()
        self.multiple_files_analyze_result_label.setText("")

        if self.tabs.currentIndex() == 0:
            if self.single_file_path is None:
                show_alert(self, "Please select a file first")
                return

            self.single_file_analyze_started = True

            if self.single_file_audio_data is None:
                self.progress_label.setText("Loading audio")
            else:
                self._start_single_file_analyze()
        else:
            if self.multiple_files_input_folder_path is None or self.multiple_files_output_folder_path is None:
                show_alert(self, "Please select input and output folders first")
                return

            self._start_multiple_file_analyze()

        self.analyze_button.setDisabled(True)
        self.progress_spinner.start()

    def on_audio_load(self, data: Tuple[np.ndarray, Union[int, float]]):
        self.single_file_audio_data = data

        if self.single_file_analyze_started:
            self._start_single_file_analyze()

    def on_analyze_result_for_single_file(self, result: pd.DataFrame):
        self.single_file_results = result
        self.single_file_result_table.set_data(result)

        if self.tabs.currentIndex() == 0:
            self.single_file_result_table.setVisible(True)

    def on_analyze_result_for_multiple_files(self, data: dict[str, Any]):
        self.multiple_files_analyze_result_label.setText(
            "Processed successfully {} file(s). There were {} error(s).".format(data["successes"], data["errors"])
        )

    def on_analyze_finished(self):
        self.single_file_analyze_started = False
        self.analyze_button.setDisabled(False)
        self.progress_spinner.stop()
        self.progress_label.setText("")

    def on_analyze_progressed(self, data: dict[str, Any]):
        if "file" in data:
            progress_text = "Processing file {}/{}".format(data["file"], data["total_files"])
            if "chunk" in data:
                progress_text += ", chunk {}/{}".format(data["chunk"], data["total_chunks"])
        else:
            progress_text = "Processing chunk {}/{}".format(data["chunk"], data["total_chunks"])

        self.progress_label.setText(progress_text)

    def on_analyze_error(self):
        show_alert(self, "An error occurred while analyzing the audio!")

    def sizeHint(self) -> QSize:
        return QSize(800, 300)

    def _start_single_file_analyze(self):
        worker = Worker(
            analyze_single_file,
            self.single_file_audio_data,
            threshold=self.threshold,
            overlap=self.overlap
        )
        worker.signals.result.connect(self.on_analyze_result_for_single_file)

        self._start_analyze_worker(worker)

    def _start_multiple_file_analyze(self):
        worker = Worker(
            analyze_multiple_files,
            self.multiple_files_input_folder_path,
            self.multiple_files_output_folder_path,
            threshold=self.threshold,
            overlap=self.overlap
        )
        worker.signals.result.connect(self.on_analyze_result_for_multiple_files)

        self._start_analyze_worker(worker)

    def _start_analyze_worker(self, worker):
        worker.signals.finished.connect(self.on_analyze_finished)
        worker.signals.progress.connect(self.on_analyze_progressed)
        worker.signals.error.connect(self.on_analyze_error)

        self.threadpool.start(worker)

    def _clear_single_file_results(self):
        self.single_file_results = None
        self.single_file_result_table.set_data(None)
        self.single_file_result_table.setVisible(False)

    def _update_analyze_button_palette(self):
        palette = self.analyze_button.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("#0f598a"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, palette.window().color())
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#73828c"))
        self.analyze_button.setPalette(palette)
