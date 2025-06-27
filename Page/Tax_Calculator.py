from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem,QSlider
)
from PySide6.QtCore import Qt

class TaxCalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💰 Tax Calculator")
        self.setGeometry(200, 100, 900, 700)

        # --- Central Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Horizontal: แบ่งซ้าย-ขวา

        # --- Left Layout (Main UI) ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(30, 30, 30, 30)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        left_layout.addWidget(self.result_text)

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter stock symbol (e.g., AAPL)")
        left_layout.addWidget(self.label_input)

        self.combo = QComboBox()
        self.combo.addItems(["Capital Gains Tax", "Dividend Tax", "Other Taxes"])
        self.combo.setPlaceholderText("Select a tax type")
        left_layout.addWidget(self.combo)


        back_to_main_btn = QPushButton("กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)
        left_layout.addWidget(back_to_main_btn)

        main_layout.addLayout(left_layout)

        # --- Right Layout (Favorites Bar) ---
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 30, 30, 30)

        self.fav_label = QLabel("⭐ Favorites")
        self.fav_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.fav_label)

        self.fav_list = QListWidget()
        # Load favorites to list (function not implemented here)
        # self.load_favorites_to_list()
        
        right_layout.addWidget(self.fav_list)

        self.Main_window = None
    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()
