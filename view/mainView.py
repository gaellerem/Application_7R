import sys, view.resources_rc
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QButtonGroup, QWidget, QLabel, QStackedWidget
from PySide6.QtCore import QFile, Qt, QIODevice


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui("view/UI/main.ui")
        self.setWindowTitle("Les 7 Royaumes")
        self.setup_ui()

    def load_ui(self, ui_file_name):
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        self.setCentralWidget(self.window)

    def setup_ui(self):
        self.stackedWidget:QStackedWidget = self.window.findChild(QStackedWidget, 'stackedWidget')
        self.change_page(0)
        for index in range(1, self.stackedWidget.count()):
            widget = self.stackedWidget.widget(index).objectName()
            self.window.findChild(QPushButton, f'{widget}_btn').clicked.connect(lambda _, index=index: self.change_page(index))
            self.window.findChild(QPushButton, f'{widget}_back').clicked.connect(lambda: self.change_page(0))

        for btn_fournisseur in self.window.findChild(QWidget, "fournisseurs").findChildren(QPushButton):
            btn_fournisseur.clicked.connect()

    def change_page(self, index:int):
        self.stackedWidget.setCurrentIndex(index)

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()