import base64
import pickle

import pandas as pd
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QWidget
from typing import Tuple, Union, Optional, Any
import numpy as np
from pathlib import Path

from functions.process_worker import ProcessWorker
from functions.worker import Worker
from functions.utils import load_audio, get_analyze_process
from functions.gui_utils import show_alert
from widgets.common.main_button import MainButton
from widgets.common.audio_drag_and_drop import AudioDragAndDrop
from widgets.audio_player.audio_player import AudioPlayer
from widgets.common.datatable import Datatable
from widgets.common.progress_label import ProgressLabel
from widgets.detector_settings import DetectorSettings


class SingleFileTab(QWidget):
    file_path = None
    audio_data: Optional[Tuple[np.ndarray, Union[int, float]]] = None

    results: Optional[pd.DataFrame] = None

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        box = QGroupBox()
        box_layout = QVBoxLayout()
        box.setLayout(box_layout)
        self.layout.addWidget(box)

        self.drag_and_drop = AudioDragAndDrop()
        self.drag_and_drop.selectedFilePath.connect(self.on_file_selected)
        box_layout.addWidget(self.drag_and_drop)

        self.audio_player = AudioPlayer()
        self.audio_player.removeClicked.connect(self.on_file_removed)
        self.audio_player.hide()
        box_layout.addWidget(self.audio_player)

        self.detector_settings = DetectorSettings()
        self.layout.addWidget(self.detector_settings)

        self.analyze_button = MainButton("Analyze")
        self.analyze_button.clicked.connect(self.on_analyze_click)
        self.layout.addWidget(self.analyze_button)

        self.progress_label = ProgressLabel()
        self.progress_label.cancelClicked.connect(self.on_cancel_analyze_click)
        self.layout.addWidget(self.progress_label)

        self.result_table = Datatable()
        self.result_table.setMinimumHeight(150)
        self.result_table.hide()
        self.layout.addWidget(self.result_table, stretch=1)

        self.layout.addStretch()

        self.analyze_worker = ProcessWorker(get_analyze_process())
        self.analyze_worker.workStatus.connect(self.on_work_status)
        self.analyze_worker.workResult.connect(self.on_work_result)
        self.analyze_worker.workError.connect(self.on_work_error)
        self.analyze_worker.workFinished.connect(self.on_work_finished)

        self.threadpool = QThreadPool()

    def update_models(self):
        self.detector_settings.update_models()

    def stop_processing(self):
        self.analyze_worker.stop_process()

    def on_file_selected(self, file_path):
        self.file_path = file_path
        self.audio_player.set_file_name(Path(file_path).name)

        self.drag_and_drop.hide()
        self.audio_player.show()
        self.audio_player.set_loading(True)

        worker = Worker(load_audio, file_path)
        worker.signals.result.connect(self.on_audio_load)
        worker.signals.error.connect(self.on_audio_load_error)

        self.threadpool.start(worker)

        self._clear_results()

    def on_file_removed(self):
        self.audio_player.hide()
        self.drag_and_drop.show()

        self.file_path = None
        self.audio_data = None
        self.audio_player.set_file_name(None)
        self.audio_player.clear_audio()

        self._clear_results()

    def on_audio_load(self, data: Tuple[np.ndarray, Union[int, float]]):
        self.audio_player.set_audio_data(self.file_path, data[0], data[1])
        self.audio_player.set_loading(False)

        self.audio_data = data

    def on_audio_load_error(self):
        show_alert(self, "Loading audio failed!")

        self.on_file_removed()

    def on_analyze_click(self):
        self._clear_results()

        if self.file_path is None:
            show_alert(self, "Please select a file first")
            return

        model_path = self.detector_settings.active_model()
        threshold = self.detector_settings.threshold()
        overlap = self.detector_settings.overlap()

        if not model_path:
            show_alert(self, "Please configure a model first")
            return

        cmd = {"cmd": "analyze_single", "file_path": self.file_path, "model_path": model_path, "threshold": threshold, "overlap": overlap}
        self.analyze_worker.start_work(cmd)

        self.analyze_button.setDisabled(True)
        self.progress_label.start_processing()
        self.progress_label.set_text("Starting worker...")

    def on_work_result(self, result: Any):
        raw = base64.b64decode(result)
        df = pickle.loads(raw)
        self.results = df
        self.result_table.set_data(df)
        self.result_table.show()

    def on_work_finished(self):
        self.analyze_button.setDisabled(False)
        self.progress_label.stop_processing()
        self.progress_label.set_text("")

    def on_work_status(self, msg: str):
        self.progress_label.set_text(msg)

    def on_work_error(self, error: str):
        show_alert(self, "An error occurred while analyzing the audio!")

    def on_cancel_analyze_click(self):
        self.progress_label.set_text("Canceling...")
        self.analyze_worker.cancel_work()

    def _clear_results(self):
        self.results = None
        self.result_table.set_data(None)
        self.result_table.hide()
