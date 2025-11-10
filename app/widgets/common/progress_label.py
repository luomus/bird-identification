from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from widgets.common.spinner import WaitingSpinner


class ProgressLabel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.progress_spinner = WaitingSpinner(self, False, lines=10, line_length=5, radius=5)
        layout.addWidget(self.progress_spinner)

        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)

    def start_spinner(self):
        self.progress_spinner.start()

    def stop_spinner(self):
        self.progress_spinner.stop()

    def set_text(self, text: str):
        self.progress_label.setText(text)
