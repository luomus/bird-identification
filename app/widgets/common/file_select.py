from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog, QHBoxLayout


class FileSelect(QWidget):
    def __init__(self, file_mode: QFileDialog.FileMode = QFileDialog.FileMode.AnyFile):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.filepath_edit = QLineEdit()
        self.filepath_edit.setMinimumHeight(25)
        layout.addWidget(self.filepath_edit)

        file_browse = QPushButton("Browse")
        file_browse.setMinimumHeight(25)
        file_browse.clicked.connect(self.on_file_browse_click)
        layout.addWidget(file_browse)

        self.dialog = QFileDialog()
        self.dialog.setWindowTitle("Select a folder")
        self.dialog.setFileMode(file_mode)
        self.dialog.setViewMode(QFileDialog.ViewMode.Detail)
        self.dialog.finished.connect(self.on_dialog_finished)

    def selected_file_path(self):
        return self.filepath_edit.text()

    def on_file_browse_click(self):
        self.dialog.open()

    def on_dialog_finished(self):
        if len(self.dialog.selectedFiles()) > 0:
            file_path = self.dialog.selectedFiles()[0]
            self.filepath_edit.setText(file_path)

    def clear(self):
        self.filepath_edit.clear()
