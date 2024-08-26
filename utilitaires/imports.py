import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import QMessageBox, QDialog
import pandas as pd
from view.choose_invoice import ChooseInvoice


def chessex(controller):
    name = "importChessex.csv"
    pathDesktop = controller.localSettings.get("path_desktop")
    data, *_ = controller.load_xls(
        filePath="",
        skiprows=range(1, 24), 
        usecols=[1, 8], 
        header=None
    )

    if data is not None:
        data = data.dropna()
        df_filtre = data[(data[1] != "Stock #") & (data[8] != 0)]
        header = ["RefInterne", "Quantité"]
        df_filtre.to_csv(
            os.path.join(pathDesktop, name),
            index=False,
            header=header,
            sep=";",
            encoding="utf-8"
        )
        QMessageBox.information(
            controller.mainWindow, 
            "Succès", f"Le fichier {name} a été créé avec succès"
        )



def invoice_item(controller):
    name = "importInvoiceItems.csv"
    pathDesktop = controller.localSettings.get("path_desktop")
    data = controller.load_csv(usecols=[3, 4, 5, 6], sep=";")

    if data is not None:
        data["Date facture"] = pd.to_datetime(
            data["Date facture"], format="%d.%m.%Y"
        )
        filter = data["Date facture"] > (datetime.now() - timedelta(days=15))
        data = data.loc[filter]
        if not data.empty:
            dialog = ChooseInvoice(controller, data["N° facture"].unique())
            dialog.show()
            if dialog.exec() != QDialog.Accepted:
                return

            factures_non_recues = dialog.get_checked_invoices()
            filter = data["N° facture"].isin(factures_non_recues)
            data = data.loc[filter]
            data[["Quantité", "Code-barres"]].to_csv(
                os.path.join(pathDesktop, name), index=False, sep=";", encoding="utf-8"
            )
            QMessageBox.information(
                controller.mainWindow, "Succès", 
                "Le fichier {name} a été créé avec succès"
            )
        else:
            QMessageBox.information(
                controller.mainWindow, "Succès", 
                "Aucunes factures de moins de 15 jours."
            )


def open_orders(controller):
    name = "importOpenOrders.csv"
    pathDesktop = controller.localSettings.get("path_desktop")
    data = controller.load_csv(usecols=[5, 11], sep=";")

    if data is not None:
        data.to_csv(
            os.path.join(pathDesktop, name), index=False, sep=";", encoding="utf-8"
        )
        QMessageBox.information(
            controller.mainWindow, "Succès", 
            f"Le fichier {name} a été créé avec succès"
        )
