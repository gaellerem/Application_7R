import os, sys

if getattr(sys, "frozen", False):
    APP_PATH = sys._MEIPASS
    EXE_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = EXE_PATH = os.path.abspath(".")

if sys.platform == "win32":
    APP_DATA = os.path.join(os.getenv('APPDATA'), 'App_7R')
elif sys.platform == "darwin":
    APP_DATA = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'App_7R')
else:
    APP_DATA = os.path.join(os.path.expanduser('~'), '.app_7R')

if not os.path.exists(APP_DATA):
    os.makedirs(APP_DATA)