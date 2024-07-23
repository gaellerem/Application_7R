from PySide6.QtWidgets import QDialog, QLineEdit, QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QLabel, QRadioButton, QButtonGroup
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


class GetDispo(QDialog):
    def __init__(self, controller, values):
        super().__init__()
        self.settings = controller.globalSettings
        self.ui = load_ui("get_dispo", controller.mainWindow)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Définir les disponibilités")
        self.values = values
        self.buttonGroups = {}
        self.setup_ui()
        self.ui.valider.clicked.connect(self.accept)

    def setup_ui(self):
        disps = {
            "Disponible": self.settings.get("dispo_dispo", []),
            "Rupture temporaire": self.settings.get("dispo_rupture", []),
            "Définitivement Epuisé": self.settings.get("dispo_epuise", []),
            "Article en précommande": self.settings.get("dispo_preco", []),
            "Incertain" : []
        }
        for value in self.values:
            layout = QHBoxLayout()
            label = QLabel()
            label.setMinimumWidth(175)
            label.setMinimumHeight(40)
            label.setText(value)
            layout.addWidget(label)
            buttonGroup = QButtonGroup(self, exclusive=True, objectName=value)
            self.buttonGroups[value] = buttonGroup
            selected_type = 'Incertain'

            for type, keywords in disps.items():
                if value in keywords:
                    selected_type = type
                    break

            for type in disps.keys():
                radio = QRadioButton()
                radio.setObjectName(f'{value}_{type}')
                radio.setMinimumWidth(102)
                if type == selected_type:
                    radio.setChecked(True)
                layout.addWidget(radio)
                buttonGroup.addButton(radio)
            self.ui.content_widget.layout().addLayout(layout)

    def get_selected_values(self):
        selected_values = {}
        for value, buttonGroup in self.buttonGroups.items():
            selected_button = buttonGroup.checkedButton()
            if selected_button:
                selected_values[value] = selected_button.objectName().split('_')[-1]
            else:
                selected_values[value] = ""
        return selected_values
