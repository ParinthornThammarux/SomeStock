from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem,QSlider
)
from PySide6.QtCore import Qt
from Fetch import Prediction
from Fetch.Manage_FAV import loadfave

class PredictionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Stock Prediction")
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
        self.combo.addItems(["RSI", "PricePrediction","Polynomial Prediction", "Hammer search", "Doji search", "EMA Cross", "PEG Ratio", "MACD"])
        self.combo.setPlaceholderText("Select an option")
        left_layout.addWidget(self.combo)

        self.predict_button = QPushButton("🔮 Predict stock")
        self.predict_button.clicked.connect(self.predict_stock)
        left_layout.addWidget(self.predict_button)

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
        self.load_favorites_to_list()
        self.fav_list.itemClicked.connect(self.favorite_clicked)
        right_layout.addWidget(self.fav_list)

        main_layout.addLayout(right_layout)

        self.Main_window = None

    def load_favorites_to_list(self):
        favorites = loadfave()
        self.fav_list.clear()
        for symbol in favorites:
            item = QListWidgetItem(symbol)
            self.fav_list.addItem(item)

    def favorite_clicked(self, item):
        self.label_input.setText(item.text())

    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()

    def predict_stock(self):
        symbol = self.label_input.text().strip()
        option = self.combo.currentText()

        self.result_text.clear()

        if option == "PricePrediction":
            success = Prediction.predict_next_price(symbol)
        elif option == "RSI":
            success = Prediction.predict_rsi(symbol)
        elif option == "Hammer search":
            success = Prediction.detect_hammer(symbol)
        elif option == "Doji search":
            success = Prediction.detect_doji(symbol)
        elif option == "EMA Cross":
            success = Prediction.detect_ema_cross(symbol)
        elif option == "PEG Ratio":
            success = Prediction.predict_peg_ratio(symbol)
        elif option == "MACD":
            success = Prediction.predict_MACD(symbol)
        elif option == "Polynomial Prediction":
            success = Prediction.predict_price_polynomial(symbol)
        else:
            success = "Invalid Option"

        self.result_text.setText(f"Prediction for {symbol} : {success:.2f}" if isinstance(success, float) else str(success))
