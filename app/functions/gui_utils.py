from PySide6.QtWidgets import QMessageBox, QWidget

def show_alert(parent: QWidget, msg: str):
    dlg = QMessageBox(parent)
    dlg.setIcon(QMessageBox.Icon.Warning)
    dlg.setWindowTitle("Alert")
    dlg.setText(msg)
    dlg.show()
