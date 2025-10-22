from typing import Optional
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtWidgets import QTableView, QHeaderView
import pandas as pd


class TableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

class Datatable(QTableView):
    model: TableModel

    def __init__(self, data: Optional[pd.DataFrame] = None):
        super().__init__()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.set_data(data)

    def set_data(self, data: Optional[pd.DataFrame] = None):
        if data is None:
            data = pd.DataFrame()

        self.model = TableModel(data)
        self.setModel(self.model)
