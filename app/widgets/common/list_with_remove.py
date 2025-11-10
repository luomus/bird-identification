from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from typing import Optional, List


class ListWithRemoveItem(QWidget):
    removeClicked = Signal()

    def __init__(self, name: str):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(name))

        layout.addStretch()

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.removeClicked)
        layout.addWidget(remove_btn)


class ListWithRemove(QWidget):
    onRemove = Signal(str)

    def __init__(self, list_items: Optional[List[str]] = None):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.model_list = QListWidget()
        self.layout.addWidget(self.model_list)

        if list_items is not None:
            for name in list_items:
                self._add_item(name)

    def set_items(self, list_items: List[str]):
        self.model_list.clear()

        for name in list_items:
            self._add_item(name)

    def on_remove_click(self, name: str):
        self.onRemove.emit(name)

    def _add_item(self, name: str):
        item = QListWidgetItem()
        widget = ListWithRemoveItem(name)
        widget.removeClicked.connect(lambda: self.on_remove_click(name))
        item.setSizeHint(widget.sizeHint())

        self.model_list.addItem(item)
        self.model_list.setItemWidget(item, widget)
