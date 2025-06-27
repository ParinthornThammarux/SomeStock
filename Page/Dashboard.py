from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QVBoxLayout, QGridLayout, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt


class DashboardWindow(QMainWindow):
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

       

        # Add stretch to push the label to the bottom

        # Windows instances
        self.second_window = None
        self.prediction_window = None
        self.Manage_window = None