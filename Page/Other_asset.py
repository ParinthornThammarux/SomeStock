from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt
from Fetch.Fetch_other import fetch_other_asset 

class OtherAssetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Daily Stock Reporter")
        self.setGeometry(200, 100, 800, 700)

        # ---------- Central Widget ----------
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(40, 40, 40, 40)

        #input frame
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        # self.ticker_entry = QLineEdit()
        # self.ticker_entry.setPlaceholderText("เช่น AAPL")
        # input_layout.addWidget(QLabel("กรอกสัญลักษณ์หุ้น (เช่น AAPL):"))
        # input_layout.addWidget(self.ticker_entry)

        # select index
        self.combo = QComboBox()
        self.combo.addItems(["^GSPC", "^HSI", "^DJI","^SET.BK"])
        self.combo.setPlaceholderText("Select an index")
        self.layout.addWidget(self.combo)
        input_frame.setLayout(input_layout)
        self.layout.addWidget(input_frame)
        
        # ---------- Output Console ----------
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)
        # make button
        self.search_button = QPushButton("🔍 ค้นหา")
        self.search_button.clicked.connect(self.fetch_asset)
        self.layout.addWidget(self.search_button)

        #back to main button
        back_to_main_btn = QPushButton("กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)
        self.layout.addWidget(back_to_main_btn)
        self.Main_window = None

    def fetch_asset(self):
        symbol = self.combo.currentText().strip()
        success = fetch_other_asset(symbol)
        self.result_text.clear()
        self.result_text.append(success.to_string())
        
        
    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()
        