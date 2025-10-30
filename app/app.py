from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap

import sys
import resources # noqa

class SplashScreen(QSplashScreen):
    isReady = Signal()

    is_ready = False

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.is_ready:
            QTimer.singleShot(0, self.isReady)
            self.is_ready = True

app = QApplication([])

splash = SplashScreen(QPixmap(":/icons/splash.png"))
splash.setEnabled(False) # clicking doesn't close it

window = None

def show_main_window():
    global window

    from widgets.main_window import MainWindow

    window = MainWindow()
    splash.finish(window)
    window.show()

splash.isReady.connect(show_main_window) # ensure that the splash screen is shown first
splash.show()

sys.exit(app.exec())
