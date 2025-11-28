from pathlib import Path
from typing import List

from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QVBoxLayout, QComboBox

from functions.utils import get_available_models
from widgets.common.input_with_label import InputWithLabel
from widgets.common.number_setting import NumberSetting


class DetectorSettings(QGroupBox):
    model_paths: List[Path] = []
    model_names: List[str] = []

    def __init__(self):
        super().__init__()

        self.setTitle("Detector Settings")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.model_select = QComboBox()
        self.update_models()
        layout.addWidget(InputWithLabel("Select model", self.model_select))

        h_box_layout = QHBoxLayout()
        layout.addLayout(h_box_layout)

        self.threshold_setting = NumberSetting(0, 1, 0.6, "Threshold")
        h_box_layout.addWidget(self.threshold_setting)

        self.overlap_setting = NumberSetting(0, 2, 0.5, "Segment overlap")
        h_box_layout.addWidget(self.overlap_setting)

    def active_model(self) -> str:
        index = self.model_names.index(self.model_select.currentText())
        return str(self.model_paths[index])

    def threshold(self) -> float:
        return self.threshold_setting.value()

    def overlap(self) -> float:
        return self.overlap_setting.value()

    def update_models(self):
        self.model_paths = get_available_models()
        self.model_names = [p.name for p in self.model_paths]

        self.model_select.clear()
        self.model_select.addItems(self.model_names)
