from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon

from widgets.common.icon_button import IconButton


class AudioInfoBar(QWidget):
    removeClick = Signal()

    def __init__(self, file_name: Optional[str]):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.file_name_label = QLabel(file_name)
        layout.addWidget(self.file_name_label)

        remove_button = IconButton(":/icons/xmark-solid-full.svg", ":/icons/xmark-solid-full-dark.svg")
        remove_button.clicked.connect(self.removeClick)
        layout.addWidget(remove_button)

    def set_file_name(self, file_name):
        self.file_name_label.setText(file_name)
