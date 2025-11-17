import shutil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from functions.utils import get_available_models, get_model_folder_path
from widgets.model_form import ModelForm
from widgets.common.list_with_remove import ListWithRemove


class ModelConfigTab(QWidget):
    modelsChanged = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Models:"))

        self.model_list = ListWithRemove(get_available_models())
        self.model_list.onRemove.connect(self.on_remove_model)
        self.layout.addWidget(self.model_list)

        self.add_button = QPushButton("Add new model")
        self.add_button.clicked.connect(self.show_form)
        self.layout.addWidget(self.add_button)

        self.form_widget = ModelForm()
        self.form_widget.cancelled.connect(self.hide_form)
        self.form_widget.submitted.connect(self.on_form_submitted)
        self.form_widget.hide()
        self.layout.addWidget(self.form_widget)

    def show_form(self):
        self.add_button.hide()
        self.form_widget.show()

    def hide_form(self):
        self.form_widget.hide()
        self.add_button.show()

    def on_remove_model(self, name: str):
        target_dir = get_model_folder_path() / name
        shutil.rmtree(target_dir)
        self.model_list.set_items(get_available_models())
        self.modelsChanged.emit()

    def on_form_submitted(self):
        self.model_list.set_items(get_available_models())
        self.hide_form()
        self.modelsChanged.emit()
