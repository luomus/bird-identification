from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QGroupBox

from widgets.common.number_setting import NumberSetting


class DetectorSettings(QGroupBox):
    thresholdChanged = Signal(float)
    overlapChanged = Signal(float)

    def __init__(self):
        super().__init__()

        self.setTitle("Detector Settings")

        layout = QHBoxLayout()
        self.setLayout(layout)

        threshold_setting = NumberSetting(0, 1, 0.6, "Threshold")
        threshold_setting.valueChanged.connect(self.thresholdChanged)
        layout.addWidget(threshold_setting)

        overlap_setting = NumberSetting(0, 2, 0.5, "Segment overlap")
        overlap_setting.valueChanged.connect(self.overlapChanged)
        layout.addWidget(overlap_setting)
