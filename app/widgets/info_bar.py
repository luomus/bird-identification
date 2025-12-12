from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from PySide6.QtCore import Qt


def get_label_with_link(text: str):
    label = QLabel(text)
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    label.setOpenExternalLinks(True)
    return label


class InfoBar(QWidget):
    def __init__(self, name: str, version: str, info_url: str, licenses_url: str):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        name_label = QLabel(name)
        font = name_label.font()
        font.setPointSize(10)
        name_label.setFont(font)
        layout.addWidget(name_label, 0, 0)

        version_label = QLabel("Version: {}".format(version))
        version_label.setFont(font)
        layout.addWidget(version_label, 1, 0)

        info_link_label = get_label_with_link("Instructions: <a href=\"{0}\">{0}</a>".format(info_url))
        info_link_label.setFont(font)
        layout.addWidget(info_link_label, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)

        licenses_link_label = get_label_with_link("Licenses: <a href=\"{0}\">{0}</a>".format(licenses_url))
        licenses_link_label.setFont(font)
        layout.addWidget(licenses_link_label, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
