from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon


class IconButton(QPushButton):
    def __init__(self, icon: QIcon):
        super().__init__(icon, "")

        self.setIconSize(QSize(25, 25))
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
