import shutil
from pathlib import Path
import json

from PySide6.QtCore import QRegularExpression, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QFileDialog

from functions.gui_utils import show_alert
from functions.utils import get_default_model_path, get_custom_model_path
from widgets.common.file_select import FileSelect


class ModelForm(QGroupBox):
    cancelled = Signal()
    submitted = Signal()

    def __init__(self):
        super().__init__()

        self.setTitle("Add new model")

        form_layout = QFormLayout()
        self.setLayout(form_layout)

        self.model_folder_select = FileSelect(QFileDialog.FileMode.Directory)
        form_layout.addRow("Model folder:", self.model_folder_select)

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
        model_folder_select_text = self.model_folder_select.selected_file_path()

        if not model_folder_select_text:
            show_alert(self, "Please select a model folder")
            return

        model_folder_path = Path(model_folder_select_text)

        if not model_folder_path.exists():
            show_alert(self, "Folder \"{}\" does not exist".format(model_folder_select_text))
            return

        name = model_folder_path.name

        default_target_dir = get_default_model_path(name)
        custom_target_dir = get_custom_model_path(name)

        if default_target_dir.exists() or custom_target_dir.exists():
            show_alert(self, "There exists already a model folder with that name")
            return

        try:
            shutil.copytree(model_folder_path, custom_target_dir)
        except Exception:
            show_alert(self, "Could not copy the model folder")
            return

        self._clear_inputs()
        self.submitted.emit()

    def _clear_inputs(self):
        self.model_folder_select.clear()
