import os, sys

if getattr(sys, "frozen", False):
    APP_PATH = sys._MEIPASS
else:
    APP_PATH = os.path.abspath(".")

APP_DATA = os.path.join(os.getenv('APPDATA'), 'App_7R')
if not os.path.exists(APP_DATA):
    os.makedirs(APP_DATA)