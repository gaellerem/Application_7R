from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QTextEdit
from models.settings import Settings
from view.mainView import MainWindow

class Controller(QObject):
    def __init__(self, mainWindow):
        super().__init__()
        self.settings = Settings()
        self.mainWindow: MainWindow = mainWindow
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.mainWindow.findChild(QPushButton, 'save_settings').clicked.connect(lambda :self.save_settings())
    def load_settings(self):
        settings_widget : QWidget = self.mainWindow.findChild(QWidget, 'settings')
        for parameter in settings_widget.findChildren(QLineEdit):
            parameter.setText(self.settings.get(parameter.objectName(), ''))
        for parameter in settings_widget.findChildren(QTextEdit):
            parameter.setPlainText(self.settings.get(parameter.objectName(), ''))

    def save_settings(self):
        settings_widget : QWidget = self.mainWindow.findChild(QWidget, 'settings')
        for parameter in settings_widget.findChildren(QLineEdit):
            self.settings[parameter.objectName()] = parameter.text()
        for parameter in settings_widget.findChildren(QTextEdit):
            self.settings[parameter.objectName()] = parameter.toPlainText()

