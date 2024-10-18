import ast
import calendar
import locale
import numpy as np
import os
from PySide6.QtWidgets import QMessageBox, QFileDialog, QDialog
from pandas import DataFrame
import pandas as pd
from view.mail_dialog import MailDialog


class Compta():
    def __init__(self, controller):
        self.controller = controller
        self.pathDesktop = controller.localSettings.get("path_desktop")
        self.FILTRE_AVOIR = list(ast.literal_eval(controller.globalSettings.get("filtre_avoir", [])))
        self.FILTRE_AUTRES = list(ast.literal_eval(controller.globalSettings.get("filtre_autres", [])))

        self.attachments = ["VENTES", "OD", "BANQUES", "CAISSES"]

    def traitement(self):
        try:
            self.get_lettrage()

            if self.lettrage is not None:
                self.directory = os.path.dirname(self.file_path)
                self.ods: dict[str:DataFrame] = {}
                self.rgm_multiple: list[tuple] = []
                self.acompte = []

                self.get_files()
                self.get_ods()
                self.save_all()

                fromAdress=self.controller.globalSettings.get("compta_from", "")
                toAdress=self.controller.globalSettings.get("compta_to", "")
                locale.setlocale(locale.LC_ALL, 'fr_FR')
                nom_mois = calendar.month_name[self.month]
                subject = f"Fichiers {nom_mois}"
                body = get_mail(self.rgm_multiple, nom_mois)
                attachments = [f"{self.directory}/{file}.csv" for file in self.attachments]

                mailDialog = MailDialog(subject, body, attachments, fromAdress, toAdress, self.controller.mainWindow)
                if mailDialog.exec() == QDialog.Accepted:
                    # Récupérer les valeurs mises à jour
                    subject, body, fromAdress, toAdress = mailDialog.get_mail_content()
                    self.controller.mail.send_email(
                        fromAdress=fromAdress,
                        toAdress=toAdress,
                        subject=subject,
                        body=body,
                        attachments=attachments
                    )

        except Exception as e:
            QMessageBox.critical(
                self.controller.mainWindow, "Erreur",
                f"Une erreur inattendue s'est produite : {e}"
            )

    def get_lettrage(self):
        self.file_path = self.controller.file_present(
            self.pathDesktop, "Lettrage")
        if not self.file_path:
            self.file_path, _ = QFileDialog.getOpenFileName(filter=("CSV (*.csv)"))
        if self.file_path:
            self.lettrage = pd.read_csv(
                self.file_path, encoding="ISO-8859-1", sep=";", dtype={"Document": str}).dropna(how="all")
            self.lettrage["Date"] = pd.to_datetime(self.lettrage["Date"], dayfirst=True, errors='coerce')
            self.lettrage = self.lettrage.sort_values(
                by="Date", ascending=False)
            self.lettrage["Document"] = self.lettrage["Document"].str.replace(
                "-", "")
            self.lettrage["Référence"] = self.lettrage["Référence"].str.replace(
                "-", "")
            self.lettrage['Document'] = np.where(self.lettrage['Document'].str.contains(
                'FAC'), self.lettrage['Document'], self.lettrage['Référence'])
        else:
            self.lettrage = None

    def get_files(self):
        def get_file(name):
            file_path = f"{self.directory}/{name}.csv"
            try:
                file = pd.read_csv(file_path, encoding="ISO-8859-1",
                                   header=None, dtype={0: str}).dropna(how="all")
                if len(file.columns) == 1:
                    file = pd.read_csv(file_path, encoding="ISO-8859-1",
                                       sep=";", header=None, dtype={0: str}).dropna(how="all")
                return file
            except FileNotFoundError:
                QMessageBox.critical(
                    self.controller.mainWindow, "Erreur",
                    f"Le fichier {file_path} n'a pas été trouvé."
                )
                return None
            except pd.errors.EmptyDataError:
                QMessageBox.critical(
                    self.controller.mainWindow, "Erreur",
                    f"Le fichier {file_path} est vide."
                )
                return None
            except Exception as e:
                QMessageBox.critical(
                    self.controller.mainWindow, "Erreur",
                    f"Une erreur inattendue s'est produite : {e}"
                )
                return None

        def check_multiple(line):
            if "/" in str(line[21]):
                temp = (line[6], line[21])
                if temp not in self.rgm_multiple:
                    self.rgm_multiple.append(temp)
                return '#MULTIPLE'
            else:
                return line[21]

        def check_dates(line):
            date_limite = pd.to_datetime(f"{self.year}-{self.month}-01")
            if isinstance(line[22], list):
                for i, date in enumerate(line[22]):
                    if date < date_limite:
                        self.acompte.append(line[21][i])

        def tri_fac_lettrage() -> DataFrame:
            # exploser en plusieurs lignes si présence de "/" dans la colonne document
            lettrage_exploded = self.lettrage.assign(
                Document=self.lettrage['Document'].str.split(' / ')).explode('Document')
            # récuperer uniquement les lignes contenant FAC
            lettrage_filtree = lettrage_exploded[lettrage_exploded['Document'].str.contains(
                'FAC', na=False)]
            # nouvelle df triée par facture avec colonne Référence et Date regroupant les RGM et dates asssociées en liste
            return lettrage_filtree.groupby('Document').agg({'Document': 'first', 'Référence': list, 'Date': list})

        self.od = get_file("OD")
        while self.od is None:
            self.od = self.controller.load_csv(
                encoding="ISO-8859-1", header=None, dtype={0: str})

        self.ventes = get_file("VENTES")
        while self.ventes is None:
            self.ventes = self.controller.load_csv(
                encoding="ISO-8859-1", header=None, dtype={0: str})

        self.banques = get_file("BANQUES")
        while self.banques is None:
            self.banques = self.controller.load_csv(
                encoding="ISO-8859-1", header=None, dtype={0: str})

        self.caisses = get_file("CAISSES")
        while self.caisses is None:
            self.caisses = self.controller.load_csv(
                encoding="ISO-8859-1", header=None, dtype={0: str})

        #mettre en capitale
        self.ventes[6] = self.ventes[6].str.upper()

        # tri par date et référence (rgm ou fac)
        for df in [self.od, self.caisses, self.banques, self.ventes]:
            df[0] = pd.to_datetime(df[0], format="%d%m%y")
            df.sort_values(by=[0, 6], ascending=[False, True], inplace=True)

        date = self.banques[0].iloc[0]
        self.month = date.month
        self.year = date.year

        for df in [self.od, self.caisses, self.banques]:  # recherche unique
            df[21] = df[6].map(
                self.lettrage.set_index("Référence")["Document"])
            df[21] = df.apply(check_multiple, axis=1)

        lettrage_factures = tri_fac_lettrage()
        self.ventes[21] = self.ventes[6].map(lettrage_factures.set_index("Document")[
                                             "Référence"]).fillna("#DIFFERE")
        self.ventes[22] = self.ventes[6].map(
            lettrage_factures.set_index("Document")["Date"]).fillna("")
        self.ventes.drop_duplicates(subset=6).apply(check_dates, axis=1)
        self.ventes[21] = self.ventes[21].apply(
            lambda liste: ' / '.join(map(str, liste)) if isinstance(liste, list) else liste)
        self.ventes = self.ventes.drop(22, axis=1)

    def get_ods(self):
        def check_multiple(line):
            if "/" in str(line["Document"]):
                temp = (line["Référence"], line["Document"])
                if temp not in self.rgm_multiple:
                    self.rgm_multiple.append(temp)
                return '#MULTIPLE'
            else:
                return line["Document"]

        def process_row(row, name):
            match name:
                case "ACOMPTES":
                    compte1 = '411'
                    compte2 = '411'
                    montant = -row["Montant"]
                    document = row["Référence"]
                case "AVOIR":
                    compte1 = '411'
                    compte2 = '411Avoir'
                    montant = row["Montant"]
                    document = None
                case "AUTRES":
                    if row["Mode de règlement"] in ["Trop perçu conservé", "Non remboursé"]:
                        compte1 = '708000'
                        compte2 = '708000'
                    else:
                        compte1 = '709700'
                        compte2 = '709700'
                    montant = row["Montant"]
                    document = None

            if montant > 0:
                od.append(dictOD(row, compte1, None, montant, document))
                od.append(dictOD(row, compte2, montant, None, None))
            else:
                od.append(dictOD(row, compte1, -montant, None, document))
                od.append(dictOD(row, compte2, None, -montant, None))

        if self.acompte:
            odacompte: DataFrame = self.lettrage[self.lettrage['Référence'].isin(
                self.acompte)]
            odacompte.loc[:, 'Date'] = odacompte['Date'].dt.strftime('%d/%m/%Y')
            self.ods["ACOMPTES"] = odacompte

        categories = ["AVOIR", "AUTRES"]
        for category in categories:
            od_df: DataFrame = self.lettrage[self.lettrage["Mode de règlement"].isin(getattr(self, f"FILTRE_{category}")) &
                                             (self.lettrage["Date"].dt.month == self.month) &
                                             (self.lettrage["Date"].dt.year == self.year)]
            if not od_df.empty:
                self.ods[category] = od_df

        for name, od_df in self.ods.items():
            od = []
            od_df.apply(process_row, axis=1, name=name)
            od_df = pd.DataFrame(od)
            od_df.insert(7, "7", value=None)
            od_df.insert(8, "8", value=None)
            for i in range(10, 20):
                od_df.insert(i, str(i), value=None)
            od_df.loc[:, "Document"] = od_df.apply(check_multiple, axis=1)
            self.ods[name] = od_df

    def save_all(self):
        self.ventes.to_csv(f'{self.directory}/VENTES.csv', header=False,
                           index=False, sep=";", encoding='ISO-8859-1')
        self.od.to_csv(f'{self.directory}/OD.csv', header=False,
                       index=False, sep=";", encoding='ISO-8859-1')
        self.banques.to_csv(f'{self.directory}/BANQUES.csv',
                            header=False, index=False, sep=";", encoding='ISO-8859-1')
        self.caisses.to_csv(f'{self.directory}/CAISSES.csv',
                            header=False, index=False, sep=";", encoding='ISO-8859-1')
        for name, df in self.ods.items():
            df.to_csv(f'{self.directory}/OD{name}.csv', header=False,
                      index=False, sep=";", encoding='ISO-8859-1')
            self.attachments.append(f'OD{name}')


def dictOD(row, compte, debit, credit, document):
    c_ou_d = 'C' if credit else 'D'
    if not document:
        document = row["Document"]
    return {'Date': row['Date'], 'Compte': compte, 'Type': 'OD',
            'Débit': debit, 'Crédit': credit, 'C_ou_D': c_ou_d,
            'Référence': row['Référence'], "Mode de règlement": row["Mode de règlement"],
            "Devise": "EUR", "Document": document}


def get_mail(rgm_multiple: list[tuple], month):
    mail = f"Bonjour Céline, \nVoici les fichiers pour {month}.\n"
    if rgm_multiple:
        for (rgm, fac) in rgm_multiple:
            mail += f"-{rgm} : {fac}\n"
    else:
        mail += "Bonne nouvelle ! Aucunes écritures à lettrer manuellement ce mois-ci.\n"
    mail += "Je te souhaites une excellente journée :)\nHugo."
    return mail
