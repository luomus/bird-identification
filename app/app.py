from PySide6.QtWidgets import QApplication
from widgets.main_window import MainWindow

app = QApplication([])

window = MainWindow()
window.show()

app.exec()
