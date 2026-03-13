import pytest

from widgets.detector_settings import DetectorSettings


@pytest.fixture
def app(qapp):
    return qapp


class TestDetectorSettings:

    def test_default_threshold(self, app, qtbot):
        settings = DetectorSettings(0.6, 0.5)
        qtbot.addWidget(settings)

        assert settings.threshold() == 0.6

    def test_default_overlap(self, app, qtbot):
        settings = DetectorSettings(0.6, 0.5)
        qtbot.addWidget(settings)

        assert settings.overlap() == 0.5

    def test_threshold_updates(self, app, qtbot):
        settings = DetectorSettings()
        qtbot.addWidget(settings)

        settings.threshold_setting.spin_box.setValue(0.8)

        assert settings.threshold() == 0.8
        assert settings.threshold_setting.slider.value() == 80

    def test_overlap_updates(self, app, qtbot):
        settings = DetectorSettings()
        qtbot.addWidget(settings)

        settings.overlap_setting.spin_box.setValue(1.0)

        assert settings.overlap() == 1.0
        assert settings.overlap_setting.slider.value() == 100
