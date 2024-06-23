import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QButtonGroup, QPushButton, QMessageBox
from PySide6.QtCore import QFile, QIODevice, Qt

def load_ui(ui_file_name, parent=None):
    ui_file = QFile(f"view/UI/{ui_file_name}.ui")
    ui_file.open(QIODevice.ReadOnly)
    loader = QUiLoader()
    widget = loader.load(ui_file, parent)
    ui_file.close()
    return widget

def show_alert(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(message)
    msg.setWindowTitle("Alerte")
    msg.exec()

def group_buttons(btnGroup:QButtonGroup, btns: list[QPushButton]):
    for btn in btns:
        btnGroup.addButton(btn)