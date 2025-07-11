from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget,
    QListWidgetItem, QFileDialog
)
from PySide6.QtCore import Qt
from Fetch import Prediction
from Fetch.Manage_FAV import loadfave

import os


class PredictionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Stock Prediction")
        self.setGeometry(200, 100, 900, 700)

        self.favorite_file = None

        # --- Central Widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Left Layout ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🔮 Stock Prediction Tool")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        left_layout.addWidget(title)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        left_layout.addWidget(self.result_text)

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter 1-2 stock symbols (e.g., AAPL,MSFT)")
        left_layout.addWidget(self.label_input)

        self.combo = QComboBox()
        self.combo.addItems([
            "RSI", "PricePrediction", "Binomial Prediction", "Hammer search", "Doji search",
            "EMA Cross", "PEG Ratio", "MACD", "Trending", "Aroon", "Sushi", "VMA", "ROC", "WILLR"
        ])
        self.combo.setPlaceholderText("Select an option")
        left_layout.addWidget(self.combo)

        self.predict_button = QPushButton("🔮 Predict stock")
        self.predict_button.clicked.connect(self.predict_stock)
        left_layout.addWidget(self.predict_button)

        back_to_main_btn = QPushButton("⬅ กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)
        left_layout.addWidget(back_to_main_btn)

        main_layout.addLayout(left_layout)

        # --- Right Layout ---
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 30, 30, 30)

        self.fav_label = QLabel("⭐ Favorites")
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
        favorites = loadfave(self.favorite_file)
        self.fav_list.clear()
        for symbol in favorites:
            item = QListWidgetItem(symbol)
            self.fav_list.addItem(item)

    def favorite_clicked(self, item):
        current = self.label_input.text().strip()
        if current:
            self.label_input.setText(f"{current},{item.text()}")
        else:
            self.label_input.setText(item.text())

    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()

    def predict_stock(self):
        symbols = [s.strip().upper() for s in self.label_input.text().split(",") if s.strip()]
        if not symbols:
            self.result_text.setText("⚠ กรุณากรอกชื่อหุ้นอย่างน้อย 1 ตัว")
            return

        option = self.combo.currentText()
        self.result_text.clear()

        for symbol in symbols:
            try:
                match option:
                    case "PricePrediction":
                        result = Prediction.predict_next_price(symbol)
                    case "RSI":
                        result = Prediction.predict_rsi(symbol)
                    case "Hammer search":
                        result = Prediction.detect_hammer(symbol)
                    case "Doji search":
                        result = Prediction.detect_doji(symbol)
                    case "EMA Cross":
                        result = Prediction.detect_ema_cross(symbol)
                    case "PEG Ratio":
                        result = Prediction.predict_peg_ratio(symbol)
                    case "MACD":
                        result = Prediction.predict_MACD(symbol)
                    case "Binomial Prediction":
                        result = Prediction.predict_price_binomial(symbol)
                    case "Trending":
                        result = Prediction.predict_momentum(symbol)
                    case "Aroon":
                        result = Prediction.predict_aroon(symbol)
                    case "Sushi":
                        result = Prediction.sushiroll(symbol)
                    case "VMA":
                        result = Prediction.VMA(symbol)
                    case "ROC":
                        result = Prediction.calculate_Roc(symbol)
                    case "WILLR":
                        result = Prediction.calculate_WILLR(symbol)
                    case _:
                        result = "❌ ไม่พบตัวเลือกที่คุณเลือก"

                display_text = f"📈 Prediction for {symbol}:\n\n{result:.2f}" if isinstance(result, float) else str(result)
                self.result_text.append(display_text)
                self.result_text.append(f"\n🛠 Method used: {option}\n{'-'*50}\n")

            except Exception as e:
                self.result_text.append(f"❌ Error with {symbol}: {str(e)}\n{'-'*50}\n")
