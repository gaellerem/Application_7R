from openpyxl import load_workbook
import os
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox

def define_quantity(row):
    qte = int(row['Qté'])
    colisage = int(row['Colisage'])
    if colisage != 1:
        qte = qte / colisage
    return qte

def gw(controller):
    pathDesktop = controller.localSettings.get("path_desktop")
    priceFilePath = controller.file_present(pathDesktop, "Liste de prix")
    if not priceFilePath:
        priceFilePath, _ = QFileDialog.getOpenFileName(filter=("XLS (*.xlsx)"), dir=pathDesktop, caption="Sélectionner la liste de prix")
    try : 
        priceList = pd.read_excel(priceFilePath, sheet_name=0, header=None, usecols=[5, 9]).dropna(axis=0, how="all")
        priceList = priceList.iloc[1:]
        priceList.rename(columns={5:"Référence", 9: "Colisage"}, inplace=True)
    except FileNotFoundError:
        return

    exportFilePath, _ = QFileDialog.getOpenFileName(filter=("CSV (*.csv)"), dir=pathDesktop, caption="Sélectionner l'export")
    try : 
        export = pd.read_csv(exportFilePath, sep=";", usecols=["Référence", "Qté"]).dropna(how="all")
    except FileNotFoundError:
        return

    results = pd.merge(priceList, export, on='Référence', how='inner')
    unfoundRefs = export[~export['Référence'].isin(results['Référence'])]
    unfoundRefs = unfoundRefs["Référence"].tolist()
    results['Qté'] = results.apply(define_quantity, axis=1)

    wb = load_workbook(priceFilePath)
    ws = wb[wb.sheetnames[0]]
    quantities = dict(zip(results["Référence"], results["Qté"]))
    for row in ws.iter_rows(max_col=ws.max_column):
        ref = row[5].value
        if ref in quantities:
            row[6].value = quantities[ref]

    # filePath = os.path.join(pathDesktop, "Commande GW.xlsx")
    # wb.save(filePath)
    wb.save()
    wb.close()
    controller.mail.send_email(
        fromAddress=controller.globalSettings.get("gw_from"),
        toAddress=controller.globalSettings.get("gw_to"),
        subject="Commande GW",
        body="Bonjour,\nCi-joint la commande de la semaine.\nBonne réception,\nHugo.",
        attachments=[priceFilePath]
    )
    controller.mail.send_email(
        fromAddress=controller.globalSettings.get("gw_from"),
        toAddress=controller.globalSettings.get("gw_errors_to"),
        subject="Erreur références GW",
        body="Bonjour,\nLes références suivantes n'ont pas été trouvées: \n -" + "\n -".join(unfoundRefs)
    )