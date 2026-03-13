import pytest

from widgets.model_config_tab import ModelConfigTab


@pytest.fixture
def app(qapp):
    return qapp


class TestModelConfigTab:

    def test_form_initially_hidden(self, app, qtbot):
        tab = ModelConfigTab()
        qtbot.addWidget(tab)

        assert tab.add_button.isVisibleTo(tab)
        assert not tab.form_widget.isVisibleTo(tab)

    def test_show_form(self, app, qtbot):
        tab = ModelConfigTab()
        qtbot.addWidget(tab)

        tab.add_button.click()

        assert not tab.add_button.isVisibleTo(tab)
        assert tab.form_widget.isVisibleTo(tab)

    def test_cancel_hides_form(self, app, qtbot):
        tab = ModelConfigTab()
        qtbot.addWidget(tab)

        tab.add_button.click()
        tab.form_widget.cancelled.emit()

        assert tab.add_button.isVisibleTo(tab)
        assert not tab.form_widget.isVisibleTo(tab)
