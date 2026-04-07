from pathlib import Path
from typing import List

from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QComboBox, QFormLayout, QWidget

from functions.utils import get_available_models
from widgets.common.number_setting import NumberSetting


class DetectorSettings(QGroupBox):
    model_paths: List[Path] = []
    model_names: List[str] = []

    def __init__(self, default_threshold: float = 0.6, default_overlap: float = 0.5):
        super().__init__()

        self.setTitle("Detector Settings")

        layout = QFormLayout()
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.setLayout(layout)

        self.model_select = QComboBox()
        self.update_models()
        layout.addRow("Select model", self.model_select)

        row_widget = QWidget()
        layout.addWidget(row_widget)

        h_box_layout = QHBoxLayout()
        h_box_layout.setSpacing(6)
        h_box_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(h_box_layout)

        self.threshold_setting = NumberSetting(0, 1, default_threshold, "Threshold")
        h_box_layout.addWidget(self.threshold_setting)

        self.overlap_setting = NumberSetting(0, 2, default_overlap, "Segment overlap")
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
