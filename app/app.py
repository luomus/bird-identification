from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

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
app_icon = QIcon()
app_icon.addFile(":/icons/bird16x16.png", QSize(16,16))
app_icon.addFile(":/icons/bird24x24.png", QSize(24,24))
app_icon.addFile(":/icons/bird32x32.png", QSize(32,32))
app_icon.addFile(":/icons/bird48x48.png", QSize(48,48))
app_icon.addFile(":/icons/bird256x256.png", QSize(256,256))
app.setWindowIcon(app_icon)

splash = SplashScreen(QPixmap(":/icons/splash.png"), Qt.WindowType.WindowStaysOnTopHint)
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
