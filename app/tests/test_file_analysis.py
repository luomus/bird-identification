import os

import pytest

from widgets.main_window import MainWindow


@pytest.fixture
def app(qapp):
    return qapp


EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), "bird.mp3")
INPUT_DIR = os.path.dirname(__file__)


class TestSingleFileAnalysis:

    def test_analyze_shows_results(self, app, qtbot):
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        tab = window.single_file_tab

        tab.drag_and_drop.selectedFilePath.emit(EXAMPLE_FILE)

        with qtbot.waitSignal(tab.analyze_worker.workResult, timeout=60_000):
            tab.analyze_button.click()

        assert tab.results is not None
        assert not tab.results.empty
        assert tab.result_table.model.rowCount(None) > 0

        tab.stop_processing()


class TestMultipleFilesAnalysis:

    def test_analyze_writes_results(self, app, qtbot, tmp_path):
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        tab = window.multiple_files_tab

        tab.input_folder_select.filepath_edit.setText(INPUT_DIR)
        tab.output_folder_select.filepath_edit.setText(str(tmp_path))

        with qtbot.waitSignal(tab.analyze_worker.workResult, timeout=60_000):
            tab.analyze_button.click()

        result_files = list(tmp_path.glob("*.results.csv"))
        assert len(result_files) > 0

        assert "1 file(s)" in tab.progress_label.get_text()
        assert "0 error(s)" in tab.progress_label.get_text()

        tab.stop_processing()
