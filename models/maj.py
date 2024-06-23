from dateutil import parser
from PySide6.QtWidgets import QPushButton, QMainWindow,QDialog
import pandas as pd
from models.manipulate_files import get_xls, file_present
from models.dfModel import DataFrameModel
from view.get_columns import GetColumns, ViewData


TYPES_COLUMNS = {"reference_fournisseur" : str,
                 "code_barre" : str,
                 "disponibilite" : str,
                 "retour_en_stock" : str,
                 "marque" : str}


def get_maj(btn:QPushButton, mainWindow:QMainWindow, settings: dict):
    def check_fournisseur(row):
        match fournisseur:
            case "tribuo":
                if "Rupture" in row["retour_en_stock"]:
                    row["disponibilite"] = "Rupture" 
                    row["retour_en_stock"] = row["retour_en_stock"].split(" - ")[-1]
                else:
                    row["disponibilite"] = "Disponible"
            case "gigamic":
                if pd.to_datetime(row["retour_en_stock"]) - pd.DateOffset(days=1) <= pd.to_datetime("now"):
                    row["disponibilite"] = "Disponible"
                else :
                    row["disponibilite"] = "Préco"
            case "iello":
                row["disponibilite"] = row["disponibilite"].split(" ", 1)[-1]
                if row["disponibilite"] == "A venir":
                    if pd.to_datetime(row["Nouveautes"]) - pd.DateOffset(days=8) <= pd.to_datetime("now"):
                        row["disponibilite"] = "Disponible"
            case "neoludis":
                if row["disponibilite"] == "":
                    row["disponibilite"] = "Incertain"
            case "pixie":
                row["reference_fournisseur"] = row["reference_fournisseur"].replace("ex ", "")
        return row
    def update_row(row):
        # row["disponibilite"] = radios[row["disponibilite"]].get()
        if row["disponibilite"] == "Disponible":
            row["retour_en_stock"] = ""

        if not confiance or (row["marque"] == "POKEMON" and fournisseur=="Asmodee") or row["disponibilite"] != "Disponible":
            row["Autoriser la vente si Hors Stock (site Web)"] = "Non"
        else:
            row["Autoriser la vente si Hors Stock (site Web)"] = "Oui"

        row["retour_en_stock"] = row["retour_en_stock"].replace(" 00:00:00", "")
        if row["retour_en_stock"] != "":
            if is_date(row["retour_en_stock"]) and pd.to_datetime(row["retour_en_stock"]) - pd.DateOffset(days=4) <= pd.to_datetime("now") and row["disponibilite"] == "Article en précommande":
                row["disponibilite"] = "Incertain"
            elif not is_date(row["retour_en_stock"]) : 
                row["retour_en_stock"] = ""
        return row

    fournisseur = btn.objectName()
    pathDesktop = settings.get("path_desktop")
    filename = settings.get(f"filename_{fournisseur}")
    columns, confiance = valeurs_fournisseurs(fournisseur)

    file_path = file_present(pathDesktop, filename)
    data, file_path = get_xls(file_path=file_path, header=None, skiprows=1)
    if data.empty : return

    #ouvrir popup pour les colonnes
    columns, confiance = get_columns(mainWindow, data, columns, confiance)

    print(columns, confiance)

def get_columns(mainWindow, data, columns, confiance):
    dialog = GetColumns(mainWindow, columns, confiance)
    dialog.show()
    viewData = ViewData(mainWindow, DataFrameModel(data.head(15)))
    viewData.show()
    if dialog.exec() != QDialog.Accepted : return
    viewData.close()
    columns, confiance = dialog.get_data()
    return columns, confiance

def valeurs_fournisseurs(fournisseur):
    columns = {}
    match fournisseur:
        case "asmodee":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "G"
            columns["retour_en_stock"] = "H"
            columns["marque"] = "D"
            confiance = True
        case "atalia":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "H"
            columns["retour_en_stock"] = "I"
            columns["marque"] = "D"
            confiance = False
        case "blackrock":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "I"
            columns["retour_en_stock"] = "J"
            columns["marque"] = "D"
            confiance = True
        case "blackrock nouveautés":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["retour_en_stock"] = "E"
            columns["marque"] = "D"
            confiance = False
        case "gigamic":
            columns["code_barre"] = "D"
            columns["reference_fournisseur"] = "C"
            columns["disponibilite"] = "I"
            columns["retour_en_stock"] = "J"
            columns["marque"] = "B"
            confiance = False
        case "heo":
            columns["code_barre"] = "E"
            columns["reference_fournisseur"] = "F"
            columns["disponibilite"] = "M"
            columns["retour_en_stock"] = "X"
            columns["marque"] = " "
            confiance = False
        case "iello":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "I"
            columns["retour_en_stock"] = "J"
            columns["marque"] = "D"
            columns["Nouveautes"]=4
            confiance = True
        case "mad":
            columns["code_barre"] = "F"
            columns["reference_fournisseur"] = "D"
            columns["disponibilite"] = "A"
            columns["retour_en_stock"] = "A"
            columns["marque"] = "B"
            confiance = False
        case "neoludis":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "I"
            columns["retour_en_stock"] = "J"
            columns["marque"] = "D"
            confiance = True
        case "novalis":
            columns["code_barre"] = "B"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "K"
            columns["retour_en_stock"] = "K"
            columns["marque"] = ""
            confiance = False
        case "pixie":
            columns["code_barre"] = "C"
            columns["reference_fournisseur"] = "A"
            columns["disponibilite"] = "I"
            columns["retour_en_stock"] = "I"
            columns["marque"] = "D"
            confiance = False
        case "tribuo":
            columns["code_barre"] = "A"
            columns["reference_fournisseur"] = "B"
            columns["disponibilite"] = "F"
            columns["retour_en_stock"] = "G"
            columns["marque"] = "C"
            confiance = False
    return columns, confiance

def is_date(value):
    try:
        parser.parse(value)
        return True
    except ValueError:
        return False