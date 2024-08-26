import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class MailManager:
    def __init__(self, path):
        # Charger la configuration depuis le fichier JSON
        self.filename = os.path.join(path, 'mailconfig.json')
        with open(self.filename, 'r') as file:
            config = json.load(file)
            self.smtpServer = config.get('smtpServer')
            self.smtpPort = config.get('smtpPort')
            self.password = config.get('password')
            self.displayName = config.get('displayName')

    def send_email(self, fromAddress, toAddress, subject, body, attachments=None):
        # Construire le message email
        msg = MIMEMultipart()
        msg['From'] = f"{self.displayName} <{fromAddress}>"
        msg['To'] = toAddress
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

        try:
            server = smtplib.SMTP(self.smtpServer, self.smtpPort)
            server.starttls()  # Démarrer le mode TLS
            server.login(fromAddress, self.password)
            text = msg.as_string()
            server.sendmail(fromAddress, toAddress, text)
            print("E-mail envoyé avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail : {e}")
        finally:
            server.quit()

