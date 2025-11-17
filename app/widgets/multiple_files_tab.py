from typing import Any, Optional

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QGroupBox

from functions.analyze import analyze_multiple_files
from functions.utils import show_alert
from functions.worker import Worker
from widgets.common.file_select import FileSelect
from widgets.common.input_with_label import InputWithLabel
from widgets.common.main_button import MainButton
from widgets.common.progress_label import ProgressLabel
from widgets.detector_settings import DetectorSettings


class MultipleFilesTab(QWidget):
    active_worker: Optional[Worker] = None

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        box = QGroupBox()
        box_layout = QVBoxLayout()
        box.setLayout(box_layout)
        self.layout.addWidget(box)

        self.input_folder_select = FileSelect(QFileDialog.FileMode.Directory)
        box_layout.addWidget(InputWithLabel("Input folder", self.input_folder_select))

        self.output_folder_select = FileSelect(QFileDialog.FileMode.Directory)
        box_layout.addWidget(InputWithLabel("Output folder", self.output_folder_select))

        self.detector_settings = DetectorSettings()
        self.layout.addWidget(self.detector_settings)

        self.analyze_button = MainButton("Analyze")
        self.analyze_button.clicked.connect(self.on_analyze_click)
        self.layout.addWidget(self.analyze_button)

        self.progress_label = ProgressLabel()
        self.progress_label.cancelClicked.connect(self.on_cancel_analyze_click)
        self.layout.addWidget(self.progress_label)

        self.layout.addStretch()

        self.threadpool = QThreadPool()

    def update_models(self):
        self.detector_settings.update_models()

    def on_analyze_click(self):
        self.progress_label.set_text("")

        input_folder_path = self.input_folder_select.selected_file_path()
        output_folder_path = self.output_folder_select.selected_file_path()

        if input_folder_path is None or output_folder_path is None:
            show_alert(self, "Please select input and output folders first")
            return

        model_folder = self.detector_settings.active_model()
        threshold = self.detector_settings.threshold()
        overlap = self.detector_settings.overlap()

        if not model_folder:
            show_alert(self, "Please configure a model first")
            return

        self._start_analyze(input_folder_path, output_folder_path, model_folder, threshold, overlap)

        self.analyze_button.setDisabled(True)
        self.progress_label.start_processing()

    def on_analyze_result(self, data: dict[str, Any]):
        self.progress_label.set_text(
            "Processed successfully {} file(s). There were {} error(s).".format(data["successes"], data["errors"])
        )

    def on_analyze_finished(self):
        self.analyze_button.setDisabled(False)
        self.progress_label.stop_processing()

    def on_analyze_progressed(self, data: dict[str, Any]):
        progress_text = "Processing file {}/{}".format(data["file"], data["total_files"])
        if "chunk" in data:
            progress_text += ", chunk {}/{}".format(data["chunk"], data["total_chunks"])

        self.progress_label.set_text(progress_text)

    def on_analyze_error(self):
        show_alert(self, "An error occurred while analyzing the audio!")
        self.progress_label.set_text("")

    def on_cancel_analyze_click(self):
        if self.active_worker is not None:
            self.active_worker.cancel()
            self.progress_label.set_text("Canceling")

    def _start_analyze(self, input_folder_path: str, output_folder_path: str, model_folder: str, threshold: float, overlap: float):
        worker = Worker(
            analyze_multiple_files,
            input_folder_path,
            output_folder_path,
            model_folder,
            threshold=threshold,
            overlap=overlap,
        )

        worker.signals.result.connect(self.on_analyze_result)
        worker.signals.finished.connect(self.on_analyze_finished)
        worker.signals.progress.connect(self.on_analyze_progressed)
        worker.signals.error.connect(self.on_analyze_error)
        self.threadpool.start(worker)

        self.active_worker = worker
