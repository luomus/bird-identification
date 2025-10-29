from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLineEdit, QLabel, QFileDialog

from pathlib import Path


class FolderSelect(QWidget):
    selectedFolderPath = Signal(str)

    def __init__(self, label: str):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(label), 0, 0)

        self.filename_edit = QLineEdit()
        self.filename_edit.setMinimumHeight(25)
        layout.addWidget(self.filename_edit, 1, 0)

        file_browse = QPushButton("Browse")
        file_browse.setMinimumHeight(25)
        file_browse.clicked.connect(self.open_file_dialog)
        layout.addWidget(file_browse, 1, 1)

        self.dialog = QFileDialog()
        self.dialog.setWindowTitle("Select a folder")
        self.dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.dialog.setViewMode(QFileDialog.ViewMode.Detail)
        self.dialog.finished.connect(self.on_finished)


    def open_file_dialog(self):
        self.dialog.open()

    def on_finished(self):
        if len(self.dialog.selectedFiles()) > 0:
            folder_path = self.dialog.selectedFiles()[0]
            self.filename_edit.setText(folder_path)
            self.selectedFolderPath.emit(folder_path)
