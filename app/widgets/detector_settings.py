from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QVBoxLayout, QComboBox

from functions.utils import get_available_models
from widgets.common.input_with_label import InputWithLabel
from widgets.common.number_setting import NumberSetting


class DetectorSettings(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setTitle("Detector Settings")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.model_select = QComboBox()
        self.model_select.addItems(get_available_models())
        layout.addWidget(InputWithLabel("Select model", self.model_select))

        h_box_layout = QHBoxLayout()
        layout.addLayout(h_box_layout)

        self.threshold_setting = NumberSetting(0, 1, 0.6, "Threshold")
        h_box_layout.addWidget(self.threshold_setting)

        self.overlap_setting = NumberSetting(0, 2, 0.5, "Segment overlap")
        h_box_layout.addWidget(self.overlap_setting)

    def active_model(self) -> str:
        return self.model_select.currentText()

    def threshold(self) -> float:
        return self.threshold_setting.value()

    def overlap(self) -> float:
        return self.overlap_setting.value()

    def update_models(self):
        self.model_select.clear()
        self.model_select.addItems(get_available_models())
