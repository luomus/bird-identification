from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QObject, QThread, Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

import sys
import resources  # noqa

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "fi.laji.birdIdentification.0.1.0"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class AppInitializerWorker(QObject):
    finished = Signal()

    def __init__(self):
        super().__init__()

    # import all heavy libraries in another thread so the app doesn't freeze while it's starting up
    def start(self):
        from functions import analyze

        self.finished.emit()


class AppInitializer(QObject):
    ready = Signal()

    def __init__(self):
        super().__init__()

        self.thread = QThread(self)

        self.worker = AppInitializerWorker()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.ready)
        self.worker.finished.connect(self.thread.quit)

        self.thread.started.connect(self.worker.start)
        self.thread.finished.connect(self.worker.deleteLater)

    def start(self):
        self.thread.start()


app = QApplication([])
app_icon = QIcon()
app_icon.addFile(":/icons/bird16x16.png", QSize(16, 16))
app_icon.addFile(":/icons/bird24x24.png", QSize(24, 24))
app_icon.addFile(":/icons/bird32x32.png", QSize(32, 32))
app_icon.addFile(":/icons/bird48x48.png", QSize(48, 48))
app_icon.addFile(":/icons/bird256x256.png", QSize(256, 256))
app.setWindowIcon(app_icon)

splash = QSplashScreen(QPixmap(":/icons/splash.png"), Qt.WindowType.WindowStaysOnTopHint)
splash.setEnabled(False)  # clicking doesn't close it
splash.show()
app.processEvents()

initializer = AppInitializer()

window = None

def show_main_window():
    global window

    from widgets.main_window import MainWindow

    window = MainWindow()
    splash.finish(window)
    window.show()

    initializer.deleteLater()

initializer.ready.connect(show_main_window)
initializer.start()

sys.exit(app.exec())
