import shutil
from pathlib import Path
import json

from PySide6.QtCore import QRegularExpression, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton

from functions.utils import show_alert, get_model_folder_path
from widgets.common.file_select import FileSelect


class ModelForm(QGroupBox):
    cancelled = Signal()
    submitted = Signal()

    name_regex = QRegularExpression(r"^[\w\s_-]+$")

    def __init__(self):
        super().__init__()

        self.setTitle("Add new model")

        form_layout = QFormLayout()
        self.setLayout(form_layout)

        self.name_edit = QLineEdit()
        validator = QRegularExpressionValidator(self.name_regex)
        self.name_edit.setValidator(validator)
        form_layout.addRow("Name:", self.name_edit)

        self.model_file_select = FileSelect()
        form_layout.addRow("Model file:", self.model_file_select)

        self.classes_file_select = FileSelect()
        form_layout.addRow("Classes file:", self.classes_file_select)

        self.calibration_file_select = FileSelect()
        form_layout.addRow("Calibration file:", self.calibration_file_select)

        btn_layout = QHBoxLayout()

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.on_save_model_click)
        btn_layout.addWidget(self.submit_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel_click)
        btn_layout.addWidget(self.cancel_btn)

        form_layout.addRow(btn_layout)

    def on_cancel_click(self):
        self._clear_inputs()
        self.cancelled.emit()

    def on_save_model_click(self):
        name = self.name_edit.text().strip()

        if name == "":
            show_alert(self, "Please enter a name for the model")
            return
        elif not self.name_regex.match(name).hasMatch():
            show_alert(self, "The name contains invalid characters")
            return

        target_dir = get_model_folder_path() / name

        if target_dir.exists():
            show_alert(self, "Please input an unique name for the model")
            return

        if not self.model_file_select.selected_file_path() or not self.classes_file_select.selected_file_path():
            show_alert(self, "Please select a model file and classes file")
            return

        model_path = Path(self.model_file_select.selected_file_path())
        classes_path = Path(self.classes_file_select.selected_file_path())

        file_paths = [model_path, classes_path]

        metadata = {
            "model_file": model_path.name,
            "classes_file": classes_path.name
        }

        if self.calibration_file_select.selected_file_path():
            calibration_path = Path(self.calibration_file_select.selected_file_path())

            file_paths.append(calibration_path)

            metadata["calibration_file"] = calibration_path.name

        for file_path in file_paths:
            if not file_path.exists():
                show_alert(self, "File \"{}\" does not exist".format(file_path))
                return

        try:
            target_dir.mkdir()
        except Exception:
            show_alert(self, "Could not create directory")
            return

        try:
            with open(target_dir / "metadata.json", "w") as f:
                json.dump(metadata, f)
        except Exception:
            show_alert(self, "Could not create metadata file")
            return


        for file_path in file_paths:
            try:
                shutil.copy(file_path, target_dir)
            except Exception:
                show_alert(self, "Could not copy file \"{}\"".format(file_path))
                shutil.rmtree(target_dir)
                return

        self._clear_inputs()
        self.submitted.emit()

    def _clear_inputs(self):
        self.name_edit.clear()
        self.model_file_select.clear()
        self.classes_file_select.clear()
        self.calibration_file_select.clear()
