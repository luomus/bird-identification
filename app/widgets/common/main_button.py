import sys

from PySide6.QtWidgets import QPushButton


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
            
            QPushButton[platform="mac"] {
                border: none;
            }
            
            QPushButton:pressed {
                background-color: rgb(24, 96, 143);
            }
            
            QPushButton:disabled {
                border: 1px solid rgb(221, 225, 227);
                background-color: transparent;
                color: #73828c;
            }
        """)
