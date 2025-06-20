"""
Qt Compatibility Layer
Provides compatibility between PyQt6 and PySide6
"""

# Removed all PyQt6 imports and usage to avoid PyInstaller Qt binding conflicts
from PySide6.QtWidgets import *
from PySide6.QtCore import Signal as pyqtSignal, QObject, QTimer, QThread, Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import *

QT_LIBRARY = "PySide6"

# Export all Qt classes
__all__ = [
    # QtWidgets
    'QApplication', 'QWidget', 'QVBoxLayout', 'QHBoxLayout', 'QLabel', 
    'QPushButton', 'QSystemTrayIcon', 'QMenu', 'QAction', 'QMessageBox',
    'QDialog', 'QTabWidget', 'QSpinBox', 'QComboBox', 'QCheckBox', 
    'QLineEdit', 'QSlider', 'QFormLayout', 'QGroupBox', 'QFileDialog',
    
    # QtCore
    'QObject', 'QTimer', 'QThread', 'pyqtSignal', 'Qt', 'QPropertyAnimation', 'QEasingCurve', 'QPoint',
    
    # QtGui
    'QIcon', 'QPixmap', 'QPainter', 'QPen', 'QFont', 'QPalette', 'QColor',
    'QLinearGradient', 'QScreen',
] 