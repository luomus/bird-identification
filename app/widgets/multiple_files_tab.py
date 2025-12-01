from typing import Any

from PySide6.QtWidgets import QVBoxLayout, QFileDialog, QGroupBox, QWidget

from functions.process_worker import ProcessWorker
from functions.gui_utils import show_alert
from functions.utils import get_analyze_process
from widgets.common.file_select import FileSelect
from widgets.common.input_with_label import InputWithLabel
from widgets.common.main_button import MainButton
from widgets.common.progress_label import ProgressLabel
from widgets.detector_settings import DetectorSettings


class MultipleFilesTab(QWidget):
    cancel_text = "Canceling..."

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

        self.analyze_worker = ProcessWorker(get_analyze_process())
        self.analyze_worker.workStatus.connect(self.on_work_status)
        self.analyze_worker.workResult.connect(self.on_work_result)
        self.analyze_worker.workError.connect(self.on_work_error)
        self.analyze_worker.workFinished.connect(self.on_work_finished)

    def update_models(self):
        self.detector_settings.update_models()

    def stop_processing(self):
        self.analyze_worker.stop_process()

    def on_analyze_click(self):
        self.progress_label.set_text("")

        input_folder_path = self.input_folder_select.selected_file_path()
        output_folder_path = self.output_folder_select.selected_file_path()

        if input_folder_path is None or output_folder_path is None:
            show_alert(self, "Please select input and output folders first")
            return

        model_path = self.detector_settings.active_model()
        threshold = self.detector_settings.threshold()
        overlap = self.detector_settings.overlap()

        if not model_path:
            show_alert(self, "Please configure a model first")
            return

        cmd = {
            "cmd": "analyze_multiple",
            "input_folder_path": input_folder_path,
            "output_folder_path": output_folder_path,
            "model_path": model_path,
            "threshold": threshold,
            "overlap": overlap
        }
        self.analyze_worker.start_work(cmd)

        self.analyze_button.setDisabled(True)
        self.progress_label.start_processing()
        self.progress_label.set_text("Starting worker...")

    def on_work_result(self, data: dict[str, Any]):
        self.progress_label.set_text(
            "Processed successfully {} file(s). There were {} error(s).".format(data["successes"], data["errors"])
        )

    def on_work_finished(self):
        self.analyze_button.setDisabled(False)
        self.progress_label.stop_processing()
        if self.progress_label.get_text() == self.cancel_text:
            self.progress_label.set_text("")

    def on_work_status(self, msg: str):
        self.progress_label.set_text(msg)

    def on_work_error(self, error: str):
        show_alert(self, "An error occurred while analyzing the audio!")
        self.progress_label.set_text("")

    def on_cancel_analyze_click(self):
        self.progress_label.set_text(self.cancel_text)
        self.analyze_worker.cancel_work()
