import os
import pandas as pd
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLineEdit, QTextEdit, QFileDialog, QInputDialog, QMessageBox
from models.mailManager import MailManager
from models.compta import Compta
from models.exports import EXP
from models.settings import Settings
from view.main_window import MainWindow
from utilitaires.gw import gw
from utilitaires.maj import get_maj
from utilitaires.imports import chessex, invoice_item, open_orders
from utilitaires.wpn import exp_wpn
from config import APP_PATH, APP_DATA


class Controller(QObject):
    def __init__(self, mainWindow):
        super().__init__()
        self.localSettinsgWidgets = ["path_desktop"]
        self.localSettings = Settings(APP_DATA)
        self.globalSettings = Settings(APP_PATH)
        self.mainWindow: MainWindow = mainWindow
        self.export = EXP(self)
        self.compta = Compta(self)
        self.mail = MailManager(APP_PATH, self)
        self.setup_ui()
        self.load_settings()

        # list(ast.literal_eval(self.globalSettings.get("dispo_dispo")))

    def setup_ui(self):
        self.mainWindow.ui.save_settings.clicked.connect(
            lambda: self.save_settings())

        self.mainWindow.maj_btns.buttonClicked.connect(
            lambda btn: get_maj(btn, self, self.globalSettings))

        self.mainWindow.ui.compta_start.clicked.connect(lambda: self.compta.traitement())

        self.mainWindow.ui.chessex.clicked.connect(lambda: chessex(self))
        self.mainWindow.ui.invoiceItem.clicked.connect(lambda: invoice_item(self))
        self.mainWindow.ui.openOrders.clicked.connect(lambda: open_orders(self))

        self.mainWindow.exp_btns.buttonClicked.connect(self.handleExport)

        self.mainWindow.ui.wpn_start.clicked.connect(lambda:exp_wpn(self))

        self.mainWindow.ui.gw_start.clicked.connect(lambda:gw(self))

        self.settings_widget = self.mainWindow.ui.settings

    def handleExport(self, button):
        button_name = button.objectName()
        exp_options = {
            "csv_asmodee": {
                "type_export": "ref_qt",
                "export_type": "csv",
                "name": "ImportAsmodeeGroup",
                "header": ["ProductId", "Quantity", "UnitOfMeasureId", "VariantId"]
            },
            "csv_blackrock": {
                "type_export": "ref_qt",
                "export_type": "csv",
                "name": "ImportBlackrock"
            },
            "xls_puzzle": {
                "type_export": "ref_qt",
                "export_type": "xls",
                "name": "ImportPuzzle.xlsx",
                "header": ["Reference", "Qty"]
            },
            "pc_gigamic": {
                "type_export": "ref_qt",
                "export_type": "paperclip",
                "name": "Gigamic",
                "separator": ","
            },
            "pc_heo": {
                "type_export": "qt_ref",
                "export_type": "paperclip",
                "name": "Heo",
                "separator": ";"
            }
        }

        if button_name in exp_options:
            options = exp_options[button_name]
            self.export.treatment(**options)

    def load_settings(self):
        for parameter in self.settings_widget.findChildren(QLineEdit):
            if parameter.objectName() in self.localSettinsgWidgets:
                parameter.setText(self.localSettings.get(
                    parameter.objectName(), ''))
            else:
                parameter.setText(self.globalSettings.get(
                    parameter.objectName(), ''))
        for parameter in self.settings_widget.findChildren(QTextEdit):
            parameter.setPlainText(
                self.globalSettings.get(parameter.objectName(), ''))

    def save_settings(self):
        for parameter in self.settings_widget.findChildren(QLineEdit):
            if parameter.objectName() in self.localSettinsgWidgets:
                self.localSettings[parameter.objectName()] = parameter.text()
            else:
                self.globalSettings[parameter.objectName()] = parameter.text()
        for parameter in self.settings_widget.findChildren(QTextEdit):
            self.globalSettings[parameter.objectName()
                                ] = parameter.toPlainText()

    def load_xls(self, filePath, **kwargs):
        if not filePath:
            path = self.localSettings.get("path_desktop", "")
            filePath, _ = QFileDialog.getOpenFileName(
                dir=path,
                filter=(
                    "fichiers Excel (*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt)"
                )
            )

        if filePath:
            try:
                xlsFile = pd.ExcelFile(filePath)
                sheetNames = xlsFile.sheet_names
                if len(sheetNames) > 1:
                    sheetName, ok = QInputDialog.getItem(
                        self.mainWindow, "Sélectionner la feuille",
                        "Choisissez une feuille:", sheetNames, 0, False
                    )
                else:
                    sheetName = sheetNames[0]
                    ok = True
                if ok and sheetName:
                    return xlsFile.parse(sheetName, **kwargs).dropna(axis=0, how="all").dropna(axis=1, how="all"), filePath
            except Exception as e:
                QMessageBox.critical(
                    self.mainWindow, "Erreur", f"Une erreur s'est produite : {e}")
        return None, filePath

    def load_csv(self, **kwargs):
        filePath, _ = QFileDialog.getOpenFileName(filter=("CSV (*.csv)"))

        if filePath:
            try:
                data = pd.read_csv(filePath, **kwargs).dropna(how="all")
                return data
            except Exception as e:
                QMessageBox.critical(
                    self.mainWindow, "Erreur", f"Une erreur s'est produite : {e}")
        return None

    def file_present(self, path, filename):
        # Liste tous les fichiers dans le chemin spécifié
        files = os.listdir(path)

        # Vérifie si le nom du fichier partiel correspond à un fichier dans le chemin donné
        for file in files:
            if filename in file:
                return os.path.join(path, file)

        # Si aucun fichier correspondant n'est trouvé
        return ""