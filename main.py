import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QVBoxLayout, QGridLayout, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt
from Page.page2 import SecondWindow
from Page.Prediction_page import PredictionWindow
from Page.Manage_Page import ManagePage
from Page.Other_asset import OtherAssetWindow
from Page.Dashboard import DashboardWindow
from Page.Tax_Calculator import TaxCalculatorWindow
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("หน้าหลัก")
        self.setGeometry(300, 200, 400, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Title
        title = QLabel("🗠 Welcome")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Grid buttons
        grid_layout = QGridLayout()

        self.open_second_btn = QPushButton("ไปหน้าที่สอง")
        self.open_third_btn = QPushButton("Manage")
        self.open_forth_btn = QPushButton("Prediction Mode")
        self.open_zero_btn = QPushButton("TEST")

        self.open_second_btn.clicked.connect(self.open_Dashboard_page)
        self.open_third_btn.clicked.connect(self.open_Manage_window)
        self.open_forth_btn.clicked.connect(self.open_prediction_window)

        grid_layout.addWidget(self.open_second_btn, 0, 0)
        grid_layout.addWidget(self.open_third_btn, 0, 1)
        grid_layout.addWidget(self.open_forth_btn, 1, 0)
        grid_layout.addWidget(self.open_zero_btn, 1, 1)
        # Dashboard button
        self.dashboard_button = QPushButton("Dashboard")
        self.dashboard_button.clicked.connect(self.dashboard_page)
        layout.addWidget(self.dashboard_button)

        # TAX button
        self.Tax_button = QPushButton("Tax Calculator")
        self.Tax_button.clicked.connect(self.open_tax_calculator)
        layout.addWidget(self.Tax_button)
        
        # Windows instances
        self.Dashboard_page = None
        self.prediction_window = None
        self.Manage_window = None
        self.Index_window = None
        self.dashboard_window = None
        self.Tax_window = None

        layout.addLayout(grid_layout)
        # Add stretch to push the label to the bottom
        layout.addStretch()

        # Bottom right label
        self.bottom_right_label = QLabel("Index && Other Info")
        self.bottom_right_label.setObjectName("INDEX")
        self.bottom_right_label.setAlignment(Qt.AlignRight)
        self.bottom_right_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.bottom_right_label.mouseDoubleClickEvent = lambda event: self.index_page()
        layout.addWidget(self.bottom_right_label)
        
        
    def open_Dashboard_page(self):
        if self.Dashboard_page is None:
            self.Dashboard_page = SecondWindow()
        self.Dashboard_page.show()
        self.hide()

    def open_prediction_window(self):
        if self.prediction_window is None:
            self.prediction_window = PredictionWindow()
        self.prediction_window.show()
        self.hide()

    def open_Manage_window(self):
        if self.Manage_window is None:
            self.Manage_window = ManagePage()
        self.Manage_window.show()
        self.hide()
    def index_page(self):
        if self.Index_window is None:
            self.Index_window = OtherAssetWindow()
        self.Index_window.show()
        self.hide()
    def dashboard_page(self):
        if self.Dashboard_page is None:
            self.Dashboard_page = DashboardWindow()
        self.Dashboard_page.show()
        self.hide()

    def open_tax_calculator(self):
        if self.Tax_window is None:
            self.Tax_window = TaxCalculatorWindow()
        self.Tax_window.show()
        self.hide()

def load_stylesheet():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "UI", "MainStyle.qss")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
