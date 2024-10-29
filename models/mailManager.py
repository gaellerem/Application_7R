from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import smtplib
from PySide6.QtWidgets import QMessageBox

class MailManager:
    def __init__(self, path, controller):
        # Charger la configuration depuis le fichier JSON
        self.filename = os.path.join(path, 'mailconfig.json')
        self.controller = controller
        self.smtpServer = controller.globalSettings.get('smtpServer')
        self.smtpPort = int(controller.globalSettings.get('smtpPort'))
        self.password = controller.globalSettings.get('password')
        self.passwordFRN = controller.globalSettings.get('password_frn')
        self.displayName = controller.globalSettings.get('displayName')

    def send_email(self, fromAdress, toAdress, subject, body, attachments=None):
        # Construire le message email
        msg = MIMEMultipart()
        msg['From'] = f"{self.displayName} <{fromAdress}>"
        msg['To'] = toAdress
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for file in attachments:
                part = MIMEBase('application', 'octet-stream')
                with open(file, 'rb') as attachment_file:
                    part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
                msg.attach(part)

        if "commande.fournisseur" in fromAdress:
            password = self.passwordFRN
        else:
            password = self.password

        try:
            server = smtplib.SMTP(self.smtpServer, self.smtpPort)
            server.starttls()  # Démarrer le mode TLS
            server.login(fromAdress, password)
            text = msg.as_string()
            server.sendmail(fromAdress, toAdress, text)
            QMessageBox.information(self.controller.mainWindow, "Succès", f"L'email a été envoyé avec succès à {toAdress}.")
        except Exception as e:
            QMessageBox.critical(self.controller.mainWindow, "Erreur", f"Une erreur s'est produite lors de l'envoi de l'e-mail : {e}")
        finally:
            server.quit()

