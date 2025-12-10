from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolButton, QApplication
from PySide6.QtGui import QIcon


class IconButton(QToolButton):
    icon_path: Optional[str] = None
    dark_icon_path: Optional[str] = None

    def __init__(self, icon_path: Optional[str] = None, dark_icon_path: Optional[str] = None):
        super().__init__()

        self.set_icon(icon_path, dark_icon_path)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(QSize(20, 20))

        QApplication.styleHints().colorSchemeChanged.connect(self.on_color_scheme_change)

    def set_icon(self, icon_path: Optional[str] = None, dark_icon_path: Optional[str] = None):
        hints = QApplication.styleHints()

        self.icon_path = icon_path
        self.dark_icon_path = dark_icon_path if dark_icon_path is not None else icon_path

        path = self.dark_icon_path if hints.colorScheme() == Qt.ColorScheme.Dark else self.icon_path
        icon = QIcon(path) if path is not None else QIcon()

        self.setIcon(icon)

    def on_color_scheme_change(self, color_scheme: Qt.ColorScheme):
        path = self.dark_icon_path if color_scheme == Qt.ColorScheme.Dark else self.icon_path
        self.setIcon(QIcon(path))
