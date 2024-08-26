import os
import pyperclip
import webbrowser
from PySide6.QtWidgets import QMessageBox


class EXP():
    def __init__(self, controller):
        self.controller = controller
        self.pathDesktop = controller.localSettings.get("path_desktop")

    def treatment(self, type_export, export_type, name="", separator="", header=False):
        self.separator = separator
        self.type_export = type_export
        self.header = header
        match export_type:
            case "csv":
                self.make_csv(name)
            case "xls":
                self.make_xls(name)
            case "paperclip":
                self.copy_to_paperclip(name)

    def make_csv(self, name):
        """
        Créé un fichier csv avec le header si spécifié
        """
        self.file_export = self.controller.load_csv(usecols=[0, 2], sep=";")
        if self.file_export is not None:
            # si un header a été spécifié et qu'il est plus long que celui du csv initial
            if self.header and len(self.header) > self.file_export.shape[1]:
                # pour toutes les colonnes après les 2 premières, les initialiser à vide
                for column in self.header[2:]:
                    self.file_export[column] = ""
            try:
                self.file_export.to_csv(
                    os.path.join(self.pathDesktop, f'{name}.csv'),
                    index=False,
                    header=self.header,
                    sep=";",
                    encoding="utf-8",
                )
                QMessageBox.information(
                    self.controller.mainWindow, "Succès",
                    f"Le fichier {name}.csv a été créé avec succès"
                )
            except PermissionError:
                QMessageBox.critical(
                    None, "Erreur", "Permission refusée. Le fichier est actuellement ouvert.")
            except Exception as e:
                QMessageBox.critical(
                    None, "Erreur", f"Une erreur s'est produite : {e}")
        match name:
            case "ImportAsmodeeGroup":
                webbrowser.open("https://shop.novalisgames.com/import")
            case "ImportBlackrock":
                webbrowser.open("https://espacepro.blackrockgames.fr/commande")

    def make_xls(self, xls_name):
        """
        Créé un fichier xls avec le header si spécifié
        """
        self.file_export = self.controller.load_csv(usecols=[0, 2], sep=";")
        if self.file_export is not None:
            try:
                self.file_export.to_excel(
                    os.path.join(self.pathDesktop, xls_name), index=False, header=self.header
                )
                QMessageBox.information(
                    self.controller.mainWindow, "Succès",
                    f"Le fichier {xls_name} a été créé avec succès"
                )
            except PermissionError:
                QMessageBox.critical(
                    None, "Erreur", "Permission refusée. Le fichier est actuellement ouvert.")
            except Exception as e:
                QMessageBox.critical(
                    None, "Erreur", f"Une erreur s'est produite : {e}")

    def copy_to_paperclip(self, name):
        """
        Récupere les données copiées du fichier d'export et les copie dans le presse-papier
        """
        self.file_export = self.controller.load_csv(usecols=[0, 2], sep=";")
        if self.file_export is not None:
            pyperclip.copy(
                self.file_export.to_csv(
                    index=False, header=self.header, sep=self.separator
                )
            )
            QMessageBox.information(self.controller.mainWindow, "Succès",
                                    "Les données ont été copiées dans le presse-papier.")
        match name:
            case "Heo":
                webbrowser.open("https://www.heo.fr/fr/fr/account/import-cart")
            case "Gigamic":
                webbrowser.open("https://commandes.gigamic.com")
