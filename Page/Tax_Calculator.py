from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from Fetch.TAX import calculate_personal_income_tax_from_foreign_gain
class TaxCalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("คำนวณภาษีเงินปันผล")
        self.setGeometry(200, 100, 400, 300)

        self.input_label = QLabel("จำนวนเงินปันผลที่ได้รับ (บาท):")
        self.dividend_input = QLineEdit()
        self.dividend_input.setPlaceholderText("เช่น 50000")

        self.calc_button = QPushButton("คำนวณภาษี")
        self.calc_button.clicked.connect(self.calculate_tax_outside)  # เชื่อมปุ่มกับฟังก์ชัน

        self.result_label = QLabel("📊 ผลลัพธ์:")

        back_to_main_btn = QPushButton("กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)

        layout = QVBoxLayout()
        layout.addWidget(self.input_label)
        layout.addWidget(self.dividend_input)
        layout.addWidget(self.calc_button)
        layout.addWidget(self.result_label)
        layout.addWidget(back_to_main_btn)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.Main_window = None
    def calculate_tax_outside(self):
        amount_text = self.dividend_input.text()
        try:
            amount = float(amount_text)
        except ValueError:
            self.result_label.setText("❌ กรุณากรอกจำนวนเงินเป็นตัวเลขเท่านั้น")
            return

        tax = calculate_personal_income_tax_from_foreign_gain(amount)
        self.result_label.setText(f"📊 ภาษีที่ต้องจ่าย: {tax:,.2f} บาท")


    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()
     