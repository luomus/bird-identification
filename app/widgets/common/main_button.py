from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QApplication
from PySide6.QtGui import QPalette, QColor, QFont


class MainButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)

        self._update_palette()
        font = self.font()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)
        self.setFixedHeight(40)

        QApplication.instance().paletteChanged.connect(self._update_palette, Qt.ConnectionType.QueuedConnection)

    def _update_palette(self):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("#0f598a"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, palette.window().color())
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#73828c"))
        self.setPalette(palette)
