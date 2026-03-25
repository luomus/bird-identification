from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, Signal, QSize, QTimer, qInstallMessageHandler
from PySide6.QtGui import QPixmap, QIcon

import sys
import resources  # noqa
from functions.qt_message_handler import qt_message_handler

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "Luomus.Sirkku"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class SplashScreen(QSplashScreen):
    isReady = Signal()

    is_ready = False

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.is_ready:
            QTimer.singleShot(0, self.isReady)
            self.is_ready = True


app = QApplication([])
qInstallMessageHandler(qt_message_handler)

app_icon = QIcon()
app_icon.addFile(":/icons/sirkku-logo16x16.png", QSize(16, 16))
app_icon.addFile(":/icons/sirkku-logo32x32.png", QSize(32, 32))
app_icon.addFile(":/icons/sirkku-logo48x48.png", QSize(48, 48))
app_icon.addFile(":/icons/sirkku-logo256x256.png", QSize(256, 256))
app.setWindowIcon(app_icon)

splash_pixmap = QPixmap(":/icons/logo/sirkku-logo-splash.png")
splash_pixmap = splash_pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

splash = SplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
splash.setEnabled(False)  # clicking doesn't close it

window = None


def show_main_window():
    global window

    from widgets.main_window import MainWindow

    window = MainWindow()
    splash.finish(window)
    window.show()


splash.isReady.connect(show_main_window)  # ensure that the splash screen is shown first
splash.show()

sys.exit(app.exec())
