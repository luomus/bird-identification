from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt


class DashedFrame(QFrame):
    def __init__(self, color="#cacaca", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setLineWidth(2)
        self.setFrameShape(QFrame.Shape.NoFrame)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)

        pen = QPen(self.color, self.lineWidth())
        pen.setDashPattern([6, 3])
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)

        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRect(rect)