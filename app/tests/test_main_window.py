import pytest

from widgets.main_window import MainWindow


@pytest.fixture
def app(qapp):
    return qapp


class TestMainWindow:

    def test_opens(self, app, qtbot):
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        assert window.isVisible()
        assert window.windowTitle() == "Sirkku"

    def test_tabs_exist(self, app, qtbot):
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        assert window.single_file_tab.isVisible()
        assert not window.multiple_files_tab.isVisible()
        assert not window.model_config_tab.isVisible()

    def test_close(self, app, qtbot):
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        window.close()
        assert not window.isVisible()
