#!/usr/bin/env python3
"""
Simple test application to verify PySide6 works
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class SimpleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add label
        label = QLabel("PySide6 is working!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Add another label
        label2 = QLabel("Desktop Screensaver Test")
        label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label2)

def main():
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 