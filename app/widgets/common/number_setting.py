from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QDoubleSpinBox


class NumberSetting(QWidget):
    valueChanged = Signal(float)

    def __init__(self, min_value:float, max_value:float, default_value:float, label:str):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel(label))

        self.spin_box = QDoubleSpinBox()
        self.spin_box.setRange(min_value, max_value)
        self.spin_box.setValue(default_value)
        self.spin_box.setSingleStep(0.01)
        self.spin_box.valueChanged.connect(self.spin_box_change)
        self.layout.addWidget(self.spin_box)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_value * 100), int(max_value * 100))
        self.slider.setValue(int(default_value * 100))
        self.slider.valueChanged.connect(self.slider_change)
        self.layout.addWidget(self.slider)

    def spin_box_change(self, value: float):
        new_slider_value = int(value * 100)
        if self.slider.value() != new_slider_value:
            self.slider.setValue(new_slider_value)

        self.valueChanged.emit(value)

    def slider_change(self, value: int):
        new_spin_box_value = round(value / 100, 2)
        if round(self.spin_box.value(), 2) != new_spin_box_value:
            self.spin_box.setValue(new_spin_box_value)
