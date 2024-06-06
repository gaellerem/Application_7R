import os
import sys

if getattr(sys, "frozen", False):
    APP_PATH = sys._MEIPASS
else:
    APP_PATH = os.path.abspath(".")