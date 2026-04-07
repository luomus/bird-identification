from PySide6.QtCore import QtMsgType, QMessageLogContext, QTimer
import logging
import sys
from functions.global_notifications import notifications


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s"
)
root_logger = logging.getLogger()


def qt_message_handler(message_type: QtMsgType, context: QMessageLogContext, message: str):
    if message_type == QtMsgType.QtCriticalMsg:
        level = logging.CRITICAL
    elif message_type == QtMsgType.QtFatalMsg:
        level = logging.ERROR
    elif message_type == QtMsgType.QtWarningMsg:
        level = logging.WARNING
        QTimer.singleShot(0, lambda: notifications.add_warning(message))
    elif message_type == QtMsgType.QtInfoMsg:
        level = logging.INFO
    elif message_type == QtMsgType.QtDebugMsg:
        level = logging.DEBUG
    else:
        level = logging.DEBUG

    root_logger.log(level, "%s", message)

    if message_type == QtMsgType.QtFatalMsg:
        sys.exit("abort")
