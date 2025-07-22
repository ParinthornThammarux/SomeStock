from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QFileDialog
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import os

from Fetch.Manage_FAV import loadfave, addfav, removefave


class ManagePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📘 Stock Manager")
        self.setGeometry(200, 100, 900, 700)
        self.favorite_file = None

        # ---------- Styling ----------
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QTextEdit {
                background-color: black;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px;
            }
            QLabel {
                font-weight: bold;
            }
        """)

        # ---------- Central Widget ----------
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ---------- Title ----------
        title = QLabel("📘 จัดการรายการโปรดของคุณ")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # ---------- File Selection ----------
        file_layout = QHBoxLayout()
        file_button = QPushButton("📁 เลือกไฟล์ .json")
        file_button.setFixedWidth(160)
        file_button.clicked.connect(self.choose_file)

        self.file_label = QLabel("⚠ ยังไม่ได้เลือกไฟล์")
        self.file_label.setStyleSheet("color: #666;")

        file_layout.addWidget(file_button)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        main_layout.addLayout(file_layout)

        # ---------- Input Section ----------
        symbol_label = QLabel("🔤 สัญลักษณ์หุ้น :")
        self.ticker_entry = QLineEdit()
        self.ticker_entry.setPlaceholderText("พิมพ์ชื่อหุ้นที่นี่...")

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ เพิ่ม")
        self.add_button.clicked.connect(self.add_favorite)

        self.remove_button = QPushButton("➖ ลบ")
        self.remove_button.clicked.connect(self.remove_favorite)
        self.remove_button.setStyleSheet("background-color: #e53935; color: white;")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        main_layout.addWidget(symbol_label)
        main_layout.addWidget(self.ticker_entry)
        main_layout.addLayout(button_layout)

        # ---------- Result Area ----------
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("⭐ รายการโปรดจะแสดงตรงนี้เมื่อคุณเลือกไฟล์")
        self.result_text.setStyleSheet("background-color: #fffbe6;")
        main_layout.addWidget(self.result_text)

        # ---------- Navigation ----------
        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("⬅ กลับไปหน้าหลัก")
        self.back_button.clicked.connect(self.open_Main_window)
        self.back_button.setStyleSheet("background-color: #607d8b; color: white;")
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_button)
        main_layout.addLayout(nav_layout)

        self.Main_window = None

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "เลือกไฟล์รายการโปรด", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.favorite_file = file_path
            self.file_label.setText(f"📄 {os.path.basename(file_path)}")
            self.refresh_favorites()

    def refresh_favorites(self):
        if not self.favorite_file:
            self.result_text.setText("⚠ กรุณาเลือกไฟล์ก่อน")
            return
        favorites = loadfave(self.favorite_file)
        if favorites:
            self.result_text.setText("⭐ รายการโปรดของคุณ:\n\n" + "\n".join(f"- {s}" for s in favorites))
        else:
            self.result_text.setText("📭 ไม่มีรายการโปรดในไฟล์นี้")

    def add_favorite(self):
        if not self.favorite_file:
            QMessageBox.warning(self, "กรุณาเลือกไฟล์", "กรุณาเลือกไฟล์ก่อนทำรายการ")
            return
        name = self.ticker_entry.text().strip().upper()
        if name:
            addfav(name, self.favorite_file)
            self.refresh_favorites()
            self.ticker_entry.clear()

    def remove_favorite(self):
        if not self.favorite_file:
            QMessageBox.warning(self, "กรุณาเลือกไฟล์", "กรุณาเลือกไฟล์ก่อนทำรายการ")
            return
        name = self.ticker_entry.text().strip().upper()
        if name:
            removefave(name, self.favorite_file)
            self.refresh_favorites()
            self.ticker_entry.clear()

    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()
