from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt

class TaxCalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("คำนวณภาษีเงินปันผล")
        self.setGeometry(200, 100, 400, 300)

        # Input field
        self.input_label = QLabel("จำนวนเงินปันผลที่ได้รับ (บาท):")
        self.dividend_input = QLineEdit()
        self.dividend_input.setPlaceholderText("เช่น 50000")

        # Button
        self.calc_button = QPushButton("คำนวณภาษี")
        # self.calc_button.clicked.connect(self.calculate_tax)

        # Output labels
        self.result_label = QLabel("📊 ผลลัพธ์:")
        self.tax_label = QLabel("")
        self.credit_label = QLabel("")
        self.net_label = QLabel("")

        # Back button
        back_to_main_btn = QPushButton("กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.input_label)
        layout.addWidget(self.dividend_input)
        layout.addWidget(self.calc_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.tax_label)
        layout.addWidget(self.credit_label)
        layout.addWidget(self.net_label)
        layout.addWidget(back_to_main_btn)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.Main_window = None

    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()
