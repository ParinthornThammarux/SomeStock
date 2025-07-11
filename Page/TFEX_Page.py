from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QVBoxLayout, QGridLayout, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt

class TFEXWINDOW(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TFEX")
        self.setGeometry(300, 200, 400, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Title
        title = QLabel("TFEX")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    


    
        back_to_main_btn = QPushButton("กลับไปหน้าหลัก")
        back_to_main_btn.clicked.connect(self.open_Main_window)
        layout.addWidget(back_to_main_btn)
        #make back function

        self.Main_window = None
    def open_Main_window(self):
        from main import MainWindow
        if self.Main_window is None:
            self.Main_window = MainWindow()
        self.Main_window.show()
        self.hide()