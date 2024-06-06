import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from controller import Controller
from view.mainView import MainWindow

class App(QApplication):
    def __init__(self):
        super(App, self).__init__()
        self.setStyle("Fusion")
        mainWindow = MainWindow()
        Controller(mainWindow)
        mainWindow.show()

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = App()
    sys.exit(app.exec())