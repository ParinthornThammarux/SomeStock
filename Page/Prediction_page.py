from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget,
    QListWidgetItem, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt
from Fetch import Prediction
from Fetch.Manage_FAV import loadfave

import os
import pandas as pd
import json


class PredictionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Stock Prediction")
        self.setGeometry(200, 100, 900, 700)
        self.favorite_file = None
        self.Main_window = None

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

        self.graph_checkbox = QCheckBox("📊 แสดงกราฟ")
        left_layout.addWidget(self.graph_checkbox)

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

        self.select_all_btn = QPushButton("📋 เลือกทั้งหมดจาก Favorites")
        self.select_all_btn.clicked.connect(self.selectall_favorites)
        right_layout.addWidget(self.select_all_btn)

        self.fav_list = QListWidget()
        self.fav_list.itemClicked.connect(self.favorite_clicked)
        right_layout.addWidget(self.fav_list)

        main_layout.addLayout(right_layout)

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

    def selectall_favorites(self):
        if not self.favorite_file:
            self.result_text.setText("⚠ ยังไม่ได้เลือกไฟล์รายการโปรด")
            return
        favorites = loadfave(self.favorite_file)
        if not favorites:
            self.result_text.setText("⚠ ไฟล์รายการโปรดว่างเปล่า")
            return
        self.label_input.setText(",".join(favorites))

    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()

    def load_json_and_predict(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "เลือกไฟล์ JSON หุ้น", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                raw_data = json.load(f)
            df = pd.DataFrame(raw_data)

            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)

            option = self.combo.currentText()
            self.result_text.clear()
            symbol = os.path.basename(file_path).split(".")[0].upper()
            show_graph = self.graph_checkbox.isChecked()

            match option:
                case "RSI":
                    result = Prediction.predict_rsi_from_df(df, plot=show_graph)
                case "MACD":
                    result = Prediction.predict_macd_from_df(df, plot=show_graph)
                case "Trending":
                    result = Prediction.predict_momentum_df(df, plot=show_graph)
                case "Aroon":
                    result = Prediction.predict_aroon_from_df(df, plot=show_graph)
                case "Hammer search":
                    result = Prediction.detect_hammer_from_df(df, plot=show_graph)
                case "Doji search":
                    result = Prediction.detect_doji_from_df(df, plot=show_graph)
                case "Sushi":
                    result = Prediction.sushiroll_from_df(df, plot=show_graph)
                case _:
                    result = "❌ ฟังก์ชันนี้ยังไม่รองรับการเรียกจาก JSON"

            self.result_text.append(f"📊 JSON Prediction for {symbol}:\n{result}\n")
            self.result_text.append(f"🧠 Method used: {option}\n{'-'*50}")

        except Exception as e:
            self.result_text.setText(f"❌ Error loading JSON: {e}")

    def predict_stock(self):
        symbols = [s.strip().upper() for s in self.label_input.text().split(",") if s.strip()]
        if not symbols:
            self.result_text.setText("⚠ กรุณากรอกชื่อหุ้นอย่างน้อย 1 ตัว")
            return

        option = self.combo.currentText()
        self.result_text.clear()
        show_graph = self.graph_checkbox.isChecked()

        for symbol in symbols:
            try:
                match option:
                    case "PricePrediction":
                        result = Prediction.predict_next_price(symbol, plot=show_graph)
                    case "RSI":
                        result = Prediction.predict_rsi(symbol, plot=show_graph)
                    case "Hammer search":
                        result = Prediction.detect_hammer(symbol, plot=show_graph)
                    case "Doji search":
                        result = Prediction.detect_doji(symbol, plot=show_graph)
                    case "EMA Cross":
                        result = Prediction.detect_ema_cross(symbol, plot=show_graph)
                    case "PEG Ratio":
                        result = Prediction.predict_peg_ratio(symbol)
                    case "MACD":
                        result = Prediction.predict_MACD(symbol, plot=show_graph)
                    case "Binomial Prediction":
                        result = Prediction.predict_price_binomial(symbol)
                    case "Trending":
                        result = Prediction.momentum(symbol, plot=show_graph)
                    case "Aroon":
                        result = Prediction.predict_aroon(symbol, plot=show_graph)
                    case "Sushi":
                        result = Prediction.sushiroll(symbol, plot=show_graph)
                    case "VMA":
                        result = Prediction.VMA(symbol, plot=show_graph)
                    case "ROC":
                        result = Prediction.calculate_Roc(symbol, plot=show_graph)
                    case "WILLR":
                        result = Prediction.calculate_WILLR(symbol, plot=show_graph)
                    case _:
                        result = "❌ ไม่พบตัวเลือกที่คุณเลือก"

                display_text = f"📈 Prediction for {symbol}:\n\n{result:.2f}" if isinstance(result, float) else str(result)
                self.result_text.append(display_text)
                self.result_text.append(f"\n🛠 Method used: {option}\n{'-'*50}\n")

            except Exception as e:
                self.result_text.append(f"❌ Error with {symbol}: {str(e)}\n{'-'*50}\n")
