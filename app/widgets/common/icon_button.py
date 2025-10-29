from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QApplication
from PySide6.QtGui import QIcon


class IconButton(QPushButton):
    def __init__(self, icon_path: str, dark_icon_path: Optional[str] = None):
        super().__init__("")

        hints = QApplication.styleHints()

        self.icon_path = icon_path
        self.dark_icon_path = dark_icon_path if dark_icon_path is not None else icon_path

        path = self.dark_icon_path if hints.colorScheme() == Qt.ColorScheme.Dark else self.icon_path

        self.setIcon(QIcon(path))
        self.setIconSize(QSize(25, 25))
        self.setMinimumSize(32, 32)
        self.setMaximumSize(32, 32)

        hints.colorSchemeChanged.connect(self.color_scheme_changed)

    def color_scheme_changed(self, color_scheme: Qt.ColorScheme):
        path = self.dark_icon_path if color_scheme == Qt.ColorScheme.Dark else self.icon_path
        self.setIcon(QIcon(path))
