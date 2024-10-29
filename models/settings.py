import json
import os
from cryptography.fernet import Fernet

SECRET_KEY = 'oyKpe9JcEBc8EDnrTJ5BfWuL-_YxCG-m4tXg3qGqYSI='

class Settings(dict):
    def __init__(self, path, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.filename = os.path.join(path, 'settings.json')
        self.cipher = Fernet(SECRET_KEY)
        self.load()

    def encrypt(self, plaintext):
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, encrypted_text):
        return self.cipher.decrypt(encrypted_text.encode()).decode()

    def load(self):
        try:
            with open(self.filename, 'r') as file:
                settings = json.load(file)
                if "password_frn" in settings:
                    settings["password_frn"] = self.decrypt(settings["password_frn"])
                if "password" in settings:
                    settings["password"] = self.decrypt(settings["password"])
                self.update(settings)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        data = {}
        for key, value in self.items():
            if 'password' in key:
                data[key] = self.encrypt(value)
            else:
                data[key] = value
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    def __setitem__(self, key, value):
        super(Settings, self).__setitem__(key, value)
        self.save()

    def __delitem__(self, key):
        super(Settings, self).__delitem__(key)
        self.save()
