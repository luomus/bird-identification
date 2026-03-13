import pytest

from widgets.common.progress_label import ProgressLabel


@pytest.fixture
def app(qapp):
    return qapp


class TestProgressLabel:

    def test_initial_state(self, app, qtbot):
        label = ProgressLabel()
        qtbot.addWidget(label)

        assert label.get_text() == ""
        assert not label.cancel_button.isVisibleTo(label)

    def test_set_and_get_text(self, app, qtbot):
        label = ProgressLabel()
        qtbot.addWidget(label)

        label.set_text("Analyzing...")
        assert label.get_text() == "Analyzing..."

    def test_start_processing_shows_cancel(self, app, qtbot):
        label = ProgressLabel()
        qtbot.addWidget(label)

        label.start_processing()

        assert label.cancel_button.isVisibleTo(label)
        assert label.spinner._is_spinning

    def test_stop_processing_hides_cancel(self, app, qtbot):
        label = ProgressLabel()
        qtbot.addWidget(label)

        label.start_processing()
        label.stop_processing()

        assert not label.cancel_button.isVisibleTo(label)
        assert not label.spinner._is_spinning

    def test_cancel_emits_signal(self, app, qtbot):
        label = ProgressLabel()
        qtbot.addWidget(label)

        label.start_processing()

        with qtbot.waitSignal(label.cancelClicked):
            label.cancel_button.click()
