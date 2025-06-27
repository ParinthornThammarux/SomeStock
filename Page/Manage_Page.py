from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame,QGridLayout
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt
from Fetch.Manage_FAV import loadfave, savefave, addfav, removefave
import json
import os

class ManagePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Stock Manager")
        self.setGeometry(200, 100, 800, 700)

        # ---------- Central Widget ----------
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # ---------- Title ----------
        title = QLabel("📈 Daily Stock Report")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # ---------- Input Section ----------
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        #Make gride for buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)

        self.ticker_entry = QLineEdit()
        self.ticker_entry.setPlaceholderText("เช่น AAPL")
        input_layout.addWidget(QLabel("กรอกสัญลักษณ์หุ้น (เช่น AAPL):"))
        input_layout.addWidget(self.ticker_entry)

        #show favorite stocks
        self.favorites = loadfave()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setText("รายการโปรดปัจจุบัน:\n" + "\n".join(self.favorites))
        self.layout.addWidget(self.result_text)

        # ADD Button
        self.addbutton = QPushButton("เพิ่มรายการโปรด")
        self.addbutton.clicked.connect(self.add_favorite)
        input_layout.addWidget(self.addbutton)
        # REMOVE Button
        self.removebutton = QPushButton("ลบรายการโปรด")
        self.removebutton.clicked.connect(self.remove_favorite)
        input_layout.addWidget(self.removebutton)

        input_frame.setLayout(input_layout)
        self.layout.addWidget(input_frame)

    # ---------- Fuction Section ----------
    def refresh_favorites(self):
        self.favorites = loadfave()
        self.result_text.setText("รายการโปรดปัจจุบัน:\n" + "\n".join(self.favorites))
    def add_favorite(self):
        name = self.ticker_entry.text().strip()
        if name:
            addfav(name)
            self.refresh_favorites()  # ✅ แก้ตรงนี้
            print(f"✅ {name} added to favorites.")
            self.ticker_entry.clear()

    def remove_favorite(self):
        name = self.ticker_entry.text().strip()
        if name:
            removefave(name)
            self.refresh_favorites()  # ✅ แก้ตรงนี้
            print(f"❌ {name} removed from favorites.")
            self.ticker_entry.clear()

    
    