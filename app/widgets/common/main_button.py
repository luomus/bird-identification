import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QApplication


class MainButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)

        self.setFixedHeight(40)

        if sys.platform == "darwin":
            platform = "mac"
        elif sys.platform == "win32":
            platform = "win"
        else:
            platform = "linux"

        self.setProperty("platform", platform)

        self.setStyleSheet("""
            QPushButton {
                border: 1px solid rgb(24, 96, 143);
                border-radius: 6px;
                
                background-color: rgb(34, 131, 195);
                color: white;
                font-size: 13pt;
                font-weight: 600;
            }
            
            QPushButton[theme="dark"] {
                border-color: rgb(22, 81, 121);
                background-color: rgb(31, 116, 173);
            }
            
            QPushButton[platform="mac"] {
                border: none;
            }
             
            QPushButton:pressed {
                background-color: rgb(24, 96, 143);
            }
            
            QPushButton:disabled {
                border: 1px solid palette(dark);
                background-color: transparent;
                color: palette(text, disabled);
            }
            
            QPushButton[theme="dark"]:disabled {
                border: 1px solid palette(midlight);
            }
        """)

        self.update_theme()
        QApplication.instance().paletteChanged.connect(self.update_theme, Qt.ConnectionType.QueuedConnection)

    def update_theme(self):
        self.setProperty("theme", "dark" if self.is_dark_mode() else "light")
        self.style().unpolish(self)
        self.style().polish(self)

    def is_dark_mode(self):
        palette = QGuiApplication.palette()
        return palette.window().color().lightness() < 128
