import json, os
from config import APP_PATH

class Settings(dict):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.filename = os.path.join(APP_PATH, 'settings.json')
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as file:
                settings = json.load(file)
                existingSettings = {k: v for k, v in settings.items() if os.path.exists(v)}
                self.update(existingSettings)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        with open(self.filename, 'w') as file:
            json.dump(self, file, indent=4)

    def __setitem__(self, key, value):
        super(Settings, self).__setitem__(key, value)
        self.save()

    def __delitem__(self, key):
        super(Settings, self).__delitem__(key)
        self.save()