import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,QGridLayout,QLabel
from Page.page2 import SecondWindow
from PySide6.QtCore import Qt
import os
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("หน้าหลัก")
        self.setGeometry(300, 200, 400, 600)

        #widget public
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        #Main Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        #build title
        title = QLabel("🗠 Welcome")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        #build grid
        grid_layout = QGridLayout()
        

        self.open_second_btn = QPushButton("ไปหน้าที่สอง")
        self.open_third_btn = QPushButton("TEST")
        self.open_forth_btn = QPushButton("TEST")
        self.open_zero_btn = QPushButton("TEST")
        
        self.open_second_btn.setMinimumHeight(40)
        self.open_second_btn.clicked.connect(self.open_second_window)

        grid_layout.addWidget(self.open_second_btn, 0, 0)
        grid_layout.addWidget(self.open_third_btn, 0, 1)
        grid_layout.addWidget(self.open_forth_btn, 1, 0)
        grid_layout.addWidget(self.open_zero_btn, 1, 1)

        layout.addLayout(grid_layout)
        self.second_window = None  # เก็บ instance หน้าที่สอง

    def open_second_window(self):
        if self.second_window is None:
            self.second_window = SecondWindow()
        self.second_window.show()
        self.hide()  # ซ่อนหน้าหลักไปเลย (ถ้าต้องการ)

def load_stylesheet():
    base_path = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ main.py
    file_path = os.path.join(base_path, "UI", "MainStyle.qss")  # รวม path
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
