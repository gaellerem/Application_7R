from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# Votre jeton d'accès OAuth 2.0
token = 'votre_jeton_d_acces'
credentials = Credentials(token)

# Construire le service Gmail API
service = build('gmail', 'v1', credentials=credentials)

# Créer un message MIME
message = MIMEText('Ceci est le corps de l\'e-mail.')
message['to'] = 'destinataire@example.com'
message['from'] = 'votre_email@gmail.com'
message['subject'] = 'Sujet de l\'e-mail'

# Encoder le message en base64
encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

# Créer le corps de la requête
body = {'raw': encoded_message}

# Envoyer l'e-mail
try:
    message = (service.users().messages().send(userId='me', body=body).execute())
    print('Message Id: %s' % message['id'])
    print("E-mail envoyé avec succès !")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'e-mail : {e}")
