from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from Fetch import StockFetch
from Generator import report_generator
import os
class SecondWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Daily Stock Reporter")
        self.resize(True,True)
        self.setGeometry(200, 100, 800, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("📈 Daily Stock Report")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        self.ticker_entry = QLineEdit()
        self.ticker_entry.setPlaceholderText("เช่น AAPL")
        input_layout.addWidget(QLabel("กรอกสัญลักษณ์หุ้น (เช่น AAPL):"))
        input_layout.addWidget(self.ticker_entry)
        
        self.combo = QComboBox()
        self.combo.addItems(["rawdata","price","EMA"])
        input_layout.addWidget(self.combo)
        
        self.search_button = QPushButton("🔍 ค้นหา")
        self.search_button.clicked.connect(self.search)
        input_layout.addWidget(self.search_button)
        self.layout.addWidget(input_frame)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.selectAll()
        self.result_text.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_text)

        self.export_button = QPushButton("📄 ส่งออก PDF")
        self.search_button.clicked.connect(self.search)

        #setup qss file
        stylesheet = self.load_stylesheet("InSide.qss")
        self.setStyleSheet(stylesheet)
        
    def load_stylesheet(self,filename):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        file_path = os.path.join(base_path,"UI", filename)  # รวม path
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    

#--------------------------------------------------------------------------------------------------------------------- 
    def search(self):
        name = self.ticker_entry.text().strip()
        select_option = self.combo.currentText()
        self.result_text.clear()

        if not name:
            self.result_text.setText("⚠️ กรุณากรอกชื่อหุ้น")
            return

        if select_option == "rawdata":
            result = StockFetch.fetch_stock_data(name)
        elif select_option == "price":
            result = StockFetch.fetch_rawdata(name)
        elif select_option == "EMA":
            result = StockFetch.calculate_MA(name)
        else:
            result = None

        if result is not None:
            try:
                result_str = result.to_string()
            except AttributeError:
                result_str = str(result)
            self.result_text.setText(result_str)
            self.result_text.selectAll()
            self.result_text.setAlignment(Qt.AlignCenter)
        else:
            self.result_text.setText("❌ ไม่สามารถดึงข้อมูลหุ้นได้")

    # def export_to_pdf(self):
    #     text = self.result_text.toPlainText().strip()
    #     if text:
    #         success = report_generator.exportpdf(text)
    #         if success:
    #             QMessageBox.information(self, "✅ สำเร็จ", "ส่งออก PDF เรียบร้อยแล้ว")
    #         else:
    #             QMessageBox.warning(self, "❌ ผิดพลาด", "ไม่สามารถส่งออก PDF ได้")
