import pytest
import pandas as pd
from PySide6.QtCore import Qt

from widgets.common.datatable import Datatable


@pytest.fixture
def app(qapp):
    return qapp


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Name": ["Sparrow", "Robin"],
        "Confidence": [0.95, 0.80],
    })


class TestDatatable:

    def test_set_data(self, app, qtbot, sample_data):
        table = Datatable()
        qtbot.addWidget(table)

        table.set_data(sample_data)

        assert table.model.rowCount(None) == 2
        assert table.model.columnCount(None) == 2

    def test_set_data_none_gives_empty_table(self, app, qtbot):
        table = Datatable()
        qtbot.addWidget(table)

        table.set_data(None)

        assert table.model.rowCount(None) == 0
        assert table.model.columnCount(None) == 0

    def test_headers(self, app, qtbot, sample_data):
        table = Datatable(sample_data)
        qtbot.addWidget(table)

        header = table.model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        assert header == "Name"

        header = table.model.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        assert header == "Confidence"

    def test_cell_values(self, app, qtbot, sample_data):
        table = Datatable(sample_data)
        qtbot.addWidget(table)

        index = table.model.index(0, 0)
        assert table.model.data(index, Qt.ItemDataRole.DisplayRole) == "Sparrow"

        index = table.model.index(1, 1)
        assert table.model.data(index, Qt.ItemDataRole.DisplayRole) == "0.8"

