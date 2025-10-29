from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QPixmap

import sys
import resources # noqa

from utils.worker import Worker

app = QApplication([])

splash = QSplashScreen(QPixmap(":/icons/splash.png"))
splash.setEnabled(False) # clicking doesn't close it
splash.show()

window = None

# MainWindow import takes a long time since it imports large libraries like tensorflow. The import is done in a separate thread so that it doesn't block the splash screen
def init_imports():
    from widgets.main_window import MainWindow # noqa

def on_ready():
    global window

    from widgets.main_window import MainWindow

    window = MainWindow()
    splash.finish(window)
    window.show()

worker = Worker(init_imports)
worker.signals.finished.connect(on_ready)

thread_pool = QThreadPool()
thread_pool.start(worker)

sys.exit(app.exec())
