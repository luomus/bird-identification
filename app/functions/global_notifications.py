from PySide6.QtCore import QObject, Signal


class GlobalNotifications(QObject):
    warnings = Signal(str)

    def add_warning(self, msg):
        self.warnings.emit(msg)

notifications = GlobalNotifications()
