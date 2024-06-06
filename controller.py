from PySide6.QtCore import QObject
from models.settings import Settings
from view.mainView import MainWindow

class Controller(QObject):
    def __init__(self, mainWindow):
        super().__init__()
        self.settings = Settings()
        self.mainWindow = mainWindow
        