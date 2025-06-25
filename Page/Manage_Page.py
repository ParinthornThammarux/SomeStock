from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt

import json
import os

FAVORITE_FILE = 'favorite_stocks.json'
def loadfave():
    with open(FAVORITE_FILE,'r') as f:
        return json.load(f)

def savefave(favorites):
    with open(FAVORITE_FILE, 'w') as f:
        json.dump(favorites, f)

def addfav(name):
    current = loadfave()
    if name not in current:
        FAVORITE_FILE.append(name)
        savefave(FAVORITE_FILE)

def removefave(name):
    current = loadfave()
    if name in current: 
        FAVORITE_FILE.remove