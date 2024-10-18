import os
from PySide6.QtWidgets import QDialog, QHBoxLayout
from utilitaires.ui import load_ui


class MailDialog(QDialog):
    def __init__(self, subject, body, attachments, fromAdress, toAdress, parent):
        super().__init__()
        self.ui = load_ui("mail", parent)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Mail")
        self.set_attachments_label(attachments)
        self.ui.fromAdress.setText(fromAdress)
        self.ui.toAdress.setText(toAdress)
        self.ui.subject.setText(subject)
        self.ui.body.setPlainText(body)

        # Connecter les boutons pour accepter ou annuler le dialog
        self.ui.accepted.connect(self.accept)
        self.ui.rejected.connect(self.reject)

    def set_attachments_label(self, attachments):
        """Affiche les noms des fichiers des pièces jointes dans le QLabel."""
        if attachments:
            # Extraire les noms de fichiers à partir des chemins
            filenames = [os.path.basename(attachment) for attachment in attachments]
            attachments_text = ", ".join(filenames)
        else:
            attachments_text = "aucunes"

        self.ui.attachments.setText(f"{attachments_text}")

    def get_mail_content(self):
        """Retourne le sujet et le corps mis à jour."""
        return self.ui.subject.text(), self.ui.body.toPlainText(), self.ui.fromAdress.text(), self.ui.toAdress.text()