from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class InputWithLabel(QWidget):
    def __init__(self, label: str, input_widget: QWidget):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(label))
        layout.addWidget(input_widget)
