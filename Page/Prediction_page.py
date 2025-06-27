from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt
from Fetch import Prediction

class PredictionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Stock Prediction")
        self.setGeometry(200, 100, 800, 700)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(40, 40, 40, 40)

        #Console for output
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        #make label input
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter stock symbol (e.g., AAPL)")
        self.layout.addWidget(self.label_input)

        #drop down optional selector
        self.combo = QComboBox()
        self.combo.addItems(["RSI", "PricePrediction", "Hammer search" , "Doji search" , "EMA Cross" ,"PEG Ratio","MACD"])
        self.combo.setPlaceholderText("Select an option")
        self.layout.addWidget(self.combo)

        #make button
        self.predict_button = QPushButton("🔮 Predict stock")
        self.predict_button.clicked.connect(self.predict_stock)
        self.layout.addWidget(self.predict_button)


        #build go back to main page button
        back_to_main_btn = QPushButton("กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)
        self.layout.addWidget(back_to_main_btn)
        #make back function
        self.Main_window = None
        
    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()

        #function to predict price
    def predict_stock(self):
            symbol = self.label_input.text().strip()
            option = self.combo.currentText()
            if(option == "PricePrediction"):
                success = Prediction.predict_next_price(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
            elif(option == "RSI"):
                success = Prediction.predict_rsi(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
            elif(option == "Hammer search"): 
                success = Prediction.detect_hammer(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
            elif(option == "Doji search"):
                success = Prediction.detect_doji(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
            elif(option == "EMA Cross"):
                success = Prediction.detect_ema_cross(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
            elif(option == "PEG Ratio"):
                success = Prediction.predict_peg_ratio(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
            elif(option == "MACD"):
                success = Prediction.predict_MACD(symbol)
                self.result_text.setText(f"Prediction for {symbol} : {success:.2f}")
    


