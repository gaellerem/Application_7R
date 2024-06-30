import ast
import pandas as pd
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QTextEdit, QFileDialog, QInputDialog, QMessageBox
from models.maj import get_maj
from models.settings import Settings
from view.mainView import MainWindow

class Controller(QObject):
    def __init__(self, mainWindow):
        super().__init__()
        self.settings = Settings()
        self.mainWindow: MainWindow = mainWindow
        self.setup_ui()
        self.load_settings()

        list(ast.literal_eval(self.settings.get("dispo_dispo")))

    def setup_ui(self):
        self.mainWindow.findChild(QPushButton, 'save_settings').clicked.connect(lambda :self.save_settings())

        self.mainWindow.maj_btns.buttonClicked.connect(lambda btn: get_maj(btn, self, self.settings))

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

    def load_xls(self, filePath, **kwargs):
        if not filePath:
            path = self.settings.get("path_desktop")
            filePath, _ = QFileDialog.getOpenFileName(dir=path,
                filter=("fichiers Excel (*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt)")
            )

        if filePath:
            try:
                xlsFile = pd.ExcelFile(filePath)
                sheetNames = xlsFile.sheet_names
                if len(sheetNames) > 1 :
                    sheetName, ok = QInputDialog.getItem(self.mainWindow, "Sélectionner la feuille", 
                                                        "Choisissez une feuille:", sheetNames, 0, False)
                else:
                    sheetName = sheetNames[0]
                    ok = True
                if ok and sheetName:
                    return xlsFile.parse(sheetName, **kwargs).dropna(axis=0, how="all").dropna(axis=1, how="all"), filePath
            except Exception as e :
                QMessageBox.critical(None, "Erreur", f"Une erreur s'est produite : {e}")
        return pd.DataFrame(), filePath

    def load_csv(self, **kwargs):
        filePath, _ = QFileDialog.getOpenFileName(filter=("CSV (*.csv)"))

        if filePath:
            try:
                data = pd.read_csv(filePath, **kwargs).dropna(how="all")
                return data
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Une erreur s'est produite : {e}")
        return None

