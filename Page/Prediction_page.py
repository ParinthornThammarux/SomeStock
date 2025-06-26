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

        #make label input
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter stock symbol (e.g., AAPL)")
        self.layout.addWidget(self.label_input)
        #make button
        self.predict_button = QPushButton("🔮 Predict Price")
        self.predict_button.clicked.connect(self.predict_price)
        self.layout.addWidget(self.predict_button)
        #drop down optional selector
        self.combo = QComboBox()
        self.combo.addItems(["RSI", "PricePrediction", "Hamme search" , "Doji search" , "EMA Cross" ,"Buffet Indicator"])
        self.combo.setPlaceholderText("Select an option")
        self.layout.addWidget(self.combo)

        #function to predict price
    def predict_price(self):
            symbol = self.label_input.text().strip()
            option = self.combo.currentText()
            if(option == "pricePrediction"):
                success = Prediction.predict_next_price(symbol)

            success  = Prediction.predict_next_price(symbol)
            if success:
                QMessageBox.information(self, "Prediction Result", f"Prediction for {symbol} completed successfully!")
            else:
                QMessageBox.warning(self, "Prediction Error", f"Failed to predict price for {symbol}. Please check the symbol and try again.")