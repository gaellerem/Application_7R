import os
from dateutil import parser
from PySide6.QtWidgets import QPushButton,QDialog
import pandas as pd
from models.dfModel import DataFrameModel
from view.maj_dialogs import GetColumns, ViewData, GetDispo


TYPES_COLUMNS = {"reference fournisseur" : str,
                 "code barre" : str,
                 "disponibilite" : str,
                 "retour en stock" : str}


def get_maj(btn:QPushButton, controller, settings: dict):
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

    filePath = file_present(pathDesktop, filename)
    data, filePath = controller.load_xls(filePath=filePath, header=None, skiprows=1)
    if data.empty : return

    #ouvrir dialog pour les colonnes
    dialog = GetColumns(controller.mainWindow, columns, confiance)
    dialog.show()
    viewData = ViewData(controller.mainWindow, DataFrameModel(data.head(15)))
    viewData.show()
    if dialog.exec() != QDialog.Accepted : return
    viewData.close()
    columns, confiance = dialog.get_data()

    #récupérer uniquement les colonnes selectionnées
    data:pd.DataFrame = data[list(columns.values())]
    data.columns= list(value.replace("_", " ") for value in columns.keys())

    #retirer les lignes où il n'y a pas de ref fournisseur
    data.dropna(subset=["reference fournisseur"], inplace=True)

    #retirer tout #NA problématique
    data["disponibilite"] = data["disponibilite"].fillna("Rupture")

    #changer le type des colonnes en str
    data = data.astype(TYPES_COLUMNS)
    data.fillna("", inplace=True)

    #effectuer des changements en fonction du fournisseur
    data = data.apply(check_fournisseur, axis=1)

    print(data)

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

def file_present(path, filename):
    # Liste tous les fichiers dans le chemin spécifié
    files = os.listdir(path)

    # Vérifie si le nom du fichier partiel correspond à un fichier dans le chemin donné
    for file in files:
        if filename in file:
            return os.path.join(path, file)
    
    # Si aucun fichier correspondant n'est trouvé
    return ""