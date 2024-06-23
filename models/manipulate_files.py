import os
import pandas as pd
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog
from view.utilitaires import show_alert


def choose_tab(sheet_names) -> str:
    def get_sheet(sheet_name: str):
        nonlocal chosen_tab
        chosen_tab = sheet_name
        window.accept()

    chosen_tab = ""
    if len(sheet_names) > 1:
        window = QDialog()
        window.setWindowTitle("Choisir la feuille")
        window.setLayout(QVBoxLayout())
        window.setStyleSheet('font-family : "Arial"; font-size : 17px;')
        for sheet_name in sheet_names:
            btn = QPushButton(str(sheet_name), window)
            window.layout().addWidget(btn)
            btn.clicked.connect(lambda _, sheet_name=sheet_name: get_sheet(sheet_name))
        window.show()
        if window.exec() == QDialog.Accepted:
            return chosen_tab
    else:
        return sheet_names[0]

def get_xls(file_path="", **kwargs) -> tuple[pd.DataFrame,str] | tuple[None, str]:
    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            filter=("fichiers Excel (*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt)")
        )

    if file_path:
        try:
            xls_file = pd.ExcelFile(file_path)
            chosen_tab = choose_tab(xls_file.sheet_names)
            if chosen_tab:
                return xls_file.parse(chosen_tab, **kwargs).dropna(axis=0, how="all").dropna(axis=1, how="all"), file_path
        except PermissionError :
            show_alert("Erreur", "Permission refusée. Merci de fermer le fichier.")
    return pd.DataFrame(), file_path

def get_csv(**kwargs) -> pd.DataFrame | None:
    """
    Ouvre une fenêtre pour choisir le fichier à traiter
    puis renvoi la dataframe avec les éventuels arguments optionnels
    """
    file_path, _ = QFileDialog.getOpenFileName(filter=("CSV (*.csv)"))

    if file_path:
        try:
            data = pd.read_csv(file_path, **kwargs).dropna(how="all")
            return data
        except Exception as e:
            show_alert("Erreur", f"Une erreur s'est produite : {e}")
    return None

def file_present(path, filename):
    # Liste tous les fichiers dans le chemin spécifié
    files = os.listdir(path)

    # Vérifie si le nom du fichier partiel correspond à un fichier dans le chemin donné
    for file in files:
        if filename in file:
            return os.path.join(path, file)
    
    # Si aucun fichier correspondant n'est trouvé
    return ""