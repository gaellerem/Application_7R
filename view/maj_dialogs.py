from PySide6.QtWidgets import QDialog, QLineEdit, QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QLabel, QRadioButton, QSizePolicy
from PySide6.QtCore import Qt
from view.utilitaires import load_ui


class GetColumns(QDialog):
    def __init__(self, parent, columns, confiance):
        super().__init__()
        self.ui = load_ui("get_columns", parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Définir les colonnes")
        self.load_data(columns, confiance)
        self.ui.valider.clicked.connect(self.validate)

    def load_data(self, columns, confiance):
        for key, value in columns.items():
            widget = self.findChild(QLineEdit, key)
            if widget : widget.setText(value)
        self.ui.confiance_oui.setChecked(confiance)
        self.ui.confiance_non.setChecked(not confiance)

    def get_data(self):
        return self.columns, self.confiance

    def validate(self):
        self.columns = {}
        for widget in self.findChildren(QLineEdit):
            text = widget.text()
            if not text and widget.objectName() != "marque":
                QMessageBox.warning(None, "Erreur", "Valeur(s) manquante(s).")
                return
            elif not text.isalpha() and widget.objectName() != "marque":
                QMessageBox.warning(None, "Erreur", "Valeur(s) incorrecte(s),\nassurez-vous que les valeurs soient une lettre.")
                return
            value = ord(text.upper())-65
            if value >= 0 :
                self.columns[widget.objectName()] = value
        self.confiance = self.ui.confiance_oui.isChecked()
        self.accept()

class ViewData(QWidget):
    def __init__(self, parent, data):
        super().__init__()
        self.ui = load_ui("view_maj", parent)
        self.setGeometry(100, 100, 1200, 300)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Données du fichier")
        self.ui.tableView.setModel(data)

