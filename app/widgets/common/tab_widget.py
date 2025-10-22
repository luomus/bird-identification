from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QTabWidget, QStackedLayout


class TabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentChanged.connect(self.updateGeometry)

    def minimumSizeHint(self):
        return self.sizeHint()

    def sizeHint(self):
        lc = QSize(0, 0)
        rc = QSize(0, 0)

        if self.cornerWidget(Qt.Corner.TopLeftCorner):
            lc = self.cornerWidget(Qt.Corner.TopLeftCorner).sizeHint()
        if self.cornerWidget(Qt.Corner.TopRightCorner):
            rc = self.cornerWidget(Qt.Corner.TopRightCorner).sizeHint()

        layout = self.findChild(QStackedLayout)
        layout_hint = layout.currentWidget().sizeHint()
        tab_hint = self.tabBar().sizeHint()

        if self.tabPosition() in (self.TabPosition.North, self.TabPosition.South):
            size = QSize(
                max(layout_hint.width(), tab_hint.width() + rc.width() + lc.width()),
                layout_hint.height() + max(rc.height(), max(lc.height(), tab_hint.height()))
            )
        else:
            size = QSize(
                layout_hint.width() + max(rc.width(), max(lc.width(), tab_hint.width())),
                max(layout_hint.height(), tab_hint.height() + rc.height() + lc.height())
            )

        return size
