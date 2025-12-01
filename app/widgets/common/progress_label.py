from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from widgets.common.spinner import WaitingSpinner


class ProgressLabel(QWidget):
    cancelClicked = Signal()

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.spinner = WaitingSpinner(self, False, lines=10, line_length=5, radius=5)
        layout.addWidget(self.spinner)

        self.label = QLabel("")
        layout.addWidget(self.label)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_click)
        self.cancel_button.hide()
        layout.addWidget(self.cancel_button)

    def start_processing(self):
        self.spinner.start()
        self.cancel_button.show()

    def stop_processing(self):
        self.spinner.stop()
        self.cancel_button.hide()

    def set_text(self, text: str):
        self.label.setText(text)

    def get_text(self):
        return self.label.text()

    def on_cancel_click(self):
        self.cancel_button.hide()
        self.cancelClicked.emit()
