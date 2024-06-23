import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from controller import Controller
from view.mainView import MainWindow

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    mainWindow = MainWindow()
    Controller(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())