from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt
from Fetch import StockFetch
from Generator import report_generator
import os

class SecondWindow(QMainWindow):
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

        # ---------- Title ----------
        title = QLabel("📈 Daily Stock Report")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # ---------- Input Section ----------
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        self.ticker_entry = QLineEdit()
        self.ticker_entry.setPlaceholderText("เช่น AAPL")
        input_layout.addWidget(QLabel("กรอกสัญลักษณ์หุ้น (เช่น AAPL):"))
        input_layout.addWidget(self.ticker_entry)

        self.combo = QComboBox()
        self.combo.addItems(["rawdata", "price", "EMA","Statement"])
        input_layout.addWidget(self.combo)

        # ---------- Result Display ----------
        self.result_text = QTextEdit(self.central_widget)
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        self.search_button = QPushButton("🔍 ค้นหา")
        self.search_button.clicked.connect(self.search)
        input_layout.addWidget(self.search_button)

        self.export_button = QPushButton("📄 ส่งออก PDF")
        self.export_button.clicked.connect(self.export_to_pdf)
        input_layout.addWidget(self.export_button)
        
        self.create_graph = QPushButton("Create Graph")
        self.create_graph.clicked.connect(self.show_the_graph)
        input_layout.addWidget(self.create_graph)

        self.layout.addWidget(input_frame)
        
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
        # ---------- Load Style ----------
        stylesheet = self.load_stylesheet("InSide.qss")
        self.setStyleSheet(stylesheet)

    def load_stylesheet(self, filename):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        file_path = os.path.join(base_path, "UI", filename)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # ---------- Search Stock ----------
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
        elif select_option == "Statement":
            result = StockFetch.financial_data(name)
        else:
            result = None

        if result is not None:
            try:
                result_str = result.to_string()
            except AttributeError:
                result_str = str(result)
            self.result_text.setText(result_str)

    # ---------- Export to PDF ----------
    def export_to_pdf(self):
        text = self.result_text.toPlainText().strip()
        if text:
            success = report_generator.exportpdf(text)
            if success:
                QMessageBox.information(self, "✅ สำเร็จ", "ส่งออก PDF เรียบร้อยแล้ว")
            else:
                QMessageBox.warning(self, "❌ ผิดพลาด", "ไม่สามารถส่งออก PDF ได้")
    #---------- Export to GRAPH ----------
    def show_the_graph(self):
        Name = self.ticker_entry.text().strip()
        if not Name:
            QMessageBox.warning(self, "⚠️ ข้อมูลไม่ครบ", "กรุณากรอกชื่อหุ้นก่อน")
            return
        success = report_generator.exportgraph(Name)
        if not success:
            QMessageBox.critical(self, "❌ ผิดพลาด", "ไม่สามารถโหลดหรือแสดงกราฟได้")