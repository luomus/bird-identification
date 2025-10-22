from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout

from widgets.common.folder_select import FolderSelect


class MultipleFileTab(QWidget):
    inputFolderChanged = Signal(str)
    outputFolderChanged = Signal(str)

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.input_folder_select = FolderSelect("Input folder")
        self.input_folder_select.selectedFolderPath.connect(self.inputFolderChanged)
        self.layout.addWidget(self.input_folder_select)

        self.output_folder_select = FolderSelect("Output folder")
        self.output_folder_select.selectedFolderPath.connect(self.outputFolderChanged)
        self.layout.addWidget(self.output_folder_select)
