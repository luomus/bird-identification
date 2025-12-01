from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabBar, QFrame
from PySide6.QtGui import QCloseEvent

from version import __version__
from widgets.info_bar import InfoBar
from widgets.model_config_tab import ModelConfigTab
from widgets.multiple_files_tab import MultipleFilesTab
from widgets.single_file_tab import SingleFileTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bird Identifier")

        widget = QWidget()
        self.setCentralWidget(widget)

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

        tab_bar = QTabBar(self)
        tab_bar.addTab("Single File")
        tab_bar.addTab("Multiple Files")
        tab_bar.addTab("Model Config")
        tab_bar.currentChanged.connect(self.on_tab_change)
        self.layout.addWidget(tab_bar)

        self.single_file_tab = SingleFileTab()
        self.layout.addWidget(self.single_file_tab)

        self.multiple_files_tab = MultipleFilesTab()
        self.layout.addWidget(self.multiple_files_tab)

        self.model_config_tab = ModelConfigTab()
        self.model_config_tab.modelsChanged.connect(self.on_models_changed)
        self.layout.addWidget(self.model_config_tab)

        self.on_tab_change(0)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

        self.info_bar = InfoBar(__version__, "https://info.laji.fi/en/sound-identification/")
        self.layout.addWidget(self.info_bar)

    def on_tab_change(self, active_idx: int):
        if active_idx == 0:
            self.multiple_files_tab.hide()
            self.model_config_tab.hide()
            self.single_file_tab.show()
        elif active_idx == 1:
            self.model_config_tab.hide()
            self.single_file_tab.hide()
            self.multiple_files_tab.show()
        elif active_idx == 2:
            self.single_file_tab.hide()
            self.multiple_files_tab.hide()
            self.model_config_tab.show()

    def on_models_changed(self):
        self.single_file_tab.update_models()
        self.multiple_files_tab.update_models()

    def sizeHint(self) -> QSize:
        return QSize(800, 300)

    def closeEvent(self, event: QCloseEvent):
        self.single_file_tab.stop_processing()
        self.multiple_files_tab.stop_processing()
        event.accept()
