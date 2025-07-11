from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt
from Fetch.Manage_FAV import loadfave
from Fetch import TFEX_Indicator as TFEX

class TFEXWINDOW(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📉 TFEX Analysis")
        self.setGeometry(250, 120, 900, 700)

        self.favorite_file = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # === Left Layout: Console + Input + Indicator ===
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("📊 TFEX Console")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        left_layout.addWidget(title)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("แสดงผลลัพธ์ของ TFEX ที่นี่...")
        left_layout.addWidget(self.console_output)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("พิมพ์ชื่อ TFEX symbol เช่น SET50")
        left_layout.addWidget(self.input_field)

        # ComboBox ตัวเลือก Indicator แบบ Prediction
        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems([
            "MA","WILLR"
        ])
        self.indicator_combo.setCurrentIndex(0)
        left_layout.addWidget(self.indicator_combo)

        self.analyze_button = QPushButton("🔍 วิเคราะห์ TFEX")
        self.analyze_button.clicked.connect(self.analyze_tfex)
        left_layout.addWidget(self.analyze_button)

        self.back_button = QPushButton("⬅ กลับไปหน้าหลัก")
        self.back_button.clicked.connect(self.open_Main_window)
        left_layout.addWidget(self.back_button)

        main_layout.addLayout(left_layout)

        # === Right Layout: Favorites ===
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 30, 30, 30)

        self.fav_label = QLabel("⭐ TFEX Favorites")
        self.fav_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.fav_label)

        self.choose_file_btn = QPushButton("📁 เลือกไฟล์รายการโปรด")
        self.choose_file_btn.clicked.connect(self.select_favorite_file)
        right_layout.addWidget(self.choose_file_btn)

        self.fav_list = QListWidget()
        self.fav_list.itemClicked.connect(self.favorite_clicked)
        right_layout.addWidget(self.fav_list)

        main_layout.addLayout(right_layout)

        self.Main_window = None

    def select_favorite_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "เลือกไฟล์รายการโปรด", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.favorite_file = file_path
            self.load_favorites_to_list()

    def load_favorites_to_list(self):
        if not self.favorite_file:
            return
        try:
            favorites = loadfave(self.favorite_file)
            self.fav_list.clear()
            for symbol in favorites:
                item = QListWidgetItem(symbol)
                self.fav_list.addItem(item)
        except Exception as e:
            self.console_output.setText(f"ไม่สามารถโหลดรายการโปรด: {e}")

    def favorite_clicked(self, item):
        self.input_field.setText(item.text())

    def analyze_tfex(self):
        symbol = self.input_field.text().strip().upper()
        indicator = self.indicator_combo.currentText()
        self.console_output.clear()

        if not symbol:
            self.console_output.setText("⚠ กรุณาใส่ชื่อ TFEX ก่อน")
            return

        # เรียกฟังก์ชันตาม indicator ที่เลือก (สมมติฟังก์ชันมีใน Prediction)
        try:
            match indicator:
                case "MA":
                    result = TFEX.MA(symbol)
                case "RSI":
                    result = TFEX.predict_rsi(symbol)
                case _:
                    result = "❌ ตัวเลือกไม่ถูกต้อง"
        except Exception as e:
            result = f"❌ เกิดข้อผิดพลาด: {e}"

        # แสดงผล
        display_text = f"📈 วิเคราะห์ {symbol} ด้วย {indicator}:\n\n"
        display_text += f"{result:.2f}" if isinstance(result, float) else str(result)
        self.console_output.setText(display_text)

    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()
