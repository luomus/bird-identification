from pathlib import Path
from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from functions.utils import get_available_models
from widgets.common.list_with_remove import ListWithRemove


class ModelList(QWidget):
    onRemove = Signal(object)

    default_models: List[Path] = []
    custom_models: List[Path] = []

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.list = ListWithRemove()
        self.list.onRemove.connect(self.on_model_removed)
        self.layout.addWidget(self.list)

        self.update_models()

    def update_models(self):
        self.list.clear()

        self.default_models = get_available_models("default")
        self.custom_models = get_available_models("custom")

        for model in self.default_models:
            self.list.add_item(model.name, False)

        for model in self.custom_models:
            self.list.add_item(model.name, True)

    def on_model_removed(self, model_name: str):
        self.onRemove.emit(self.get_model_by_name(model_name))

    def get_model_by_name(self, model_name: str) -> Path:
        for model in self.default_models:
            if model.name == model_name:
                return model

        for model in self.custom_models:
            if model.name == model_name:
                return model

