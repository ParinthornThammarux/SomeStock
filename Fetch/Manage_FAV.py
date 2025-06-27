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
    if not os.path.exists(FAVORITE_FILE):
        return []  # ถ้าไฟล์ยังไม่มี ให้เริ่มจากลิสต์ว่าง
    with open(FAVORITE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # ถ้าไฟล์ว่างหรือไม่ใช่ JSON ถูก ให้คืนค่าเป็นลิสต์ว่าง

def savefave(favorites):
    with open(FAVORITE_FILE, 'w') as f:
        json.dump(favorites, f)

def addfav(name):
    current = loadfave()
    if name not in current:
        current.append(name)
        savefave(current)

def removefave(name):
    current = loadfave()
    if name in current: 
        current.remove(name)
        savefave(current)