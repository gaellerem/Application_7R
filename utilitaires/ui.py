from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QButtonGroup, QPushButton
from PySide6.QtCore import QFile, QIODevice

def load_ui(ui_file_name, parent=None):
    ui_file = QFile(f"view/UI/{ui_file_name}.ui")
    ui_file.open(QIODevice.ReadOnly)
    loader = QUiLoader()
    widget = loader.load(ui_file, parent)
    ui_file.close()
    return widget

def group_buttons(btnGroup:QButtonGroup, btns: list[QPushButton]):
    for btn in btns:
        btnGroup.addButton(btn)