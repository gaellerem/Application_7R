import os
import pandas as pd
from PySide6.QtWidgets import QDialog
from view.mail_dialog import MailDialog

TYPES = {
        "Date et heure du document": str,
        "Réf. LMB du document": str,
        "Codes-barres": str,
        "Réf. fournisseur favori de l'article": str,
        "Réf. interne de l'article": str,
        "Marque": str,
        "Libellé de l'article": str,
        "Quantité": str,
        "Prix unitaire HT de l'article": str,
        "Montant total de la ligne de vente HT": str,
        "Devise": str,
        }

def exp_wpn(controller):
    def modifs():
        nonlocal wpn_file
        # sectionner la colonne 'Date et heure du document' en deux
        wpn_date_hour = wpn_file["Date et heure du document"].str.split(" ", expand=True)

        # ajouter les colonnes ID, Date et Heure
        wpn_file.insert(0, "ID", pd.Series("5783", index=wpn_file.index))
        wpn_file.insert(1, "Date", wpn_date_hour[0])
        wpn_file.insert(2, "Heure", wpn_date_hour[1])
        #supprimer les secondes de l'heure
        wpn_file["Heure"] = wpn_file["Heure"].str.rsplit(":", n=1).str[0]
        # supprimer la colonne 'Date et heure du document'
        wpn_file = wpn_file.drop("Date et heure du document", axis=1)
        # trier les marques
        wpn_file = wpn_file.query('Marque == "Magic The Gathering" or Marque == "Wizards of the Coast"')
        # trier par date  et heure croissante
        wpn_file = wpn_file.sort_values(["Date", "Heure"])

    pathDesktop = controller.localSettings.get("path_desktop")
    wpn_file = controller.load_csv(encoding="ISO-8859-1", skip_blank_lines=True, dtype='str', sep=";")
    if wpn_file is not None:
        modifs()

        month, year = wpn_file.iloc[0, 1].split("/")[1:]
        file_name = "5783_Les7Royaumes_POSData_" + month + year[-2:] + ".csv"

        wpn_file.to_csv(os.path.join(pathDesktop, file_name), index=False, sep=";", encoding="utf-8")

        fromAdress=controller.globalSettings.get("wpn_from", "")
        toAdress=controller.globalSettings.get("wpn_to", "")
        subject = "WPN POS DATA 5783"
        body = "Bonjour,\nVoici le fichier demandé.\nBonne réception,\nHugo."
        attachments = [os.path.join(pathDesktop, file_name)]

        mailDialog = MailDialog(subject, body, attachments, fromAdress, toAdress, controller.mainWindow)
        if mailDialog.exec() == QDialog.Accepted:
            # Récupérer les valeurs mises à jour
            subject, body, fromAdress, toAdress = mailDialog.get_mail_content()
            controller.mail.send_email(
                fromAdress=fromAdress,
                toAdress=toAdress,
                subject=subject,
                body=body,
                attachments=attachments
            )


