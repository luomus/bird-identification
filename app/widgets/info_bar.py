from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class InfoBar(QWidget):
    def __init__(self, version: str, info_url: str):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        version_label = QLabel("Version: {}".format(version))
        font = version_label.font()
        font.setPointSize(10)
        version_label.setFont(font)
        layout.addWidget(version_label)

        layout.addStretch()

        info_link_label = QLabel("Instructions: <a href=\"{0}\">{0}</a>".format(info_url))
        info_link_label.setTextFormat(Qt.TextFormat.RichText)
        info_link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info_link_label.setOpenExternalLinks(True)
        info_link_label.setFont(font)
        layout.addWidget(info_link_label)
