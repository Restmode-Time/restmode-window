"""
Main Application Window (Guest Interface)
Provides a simplified interface for status and basic controls
"""

import logging
from src.utils.qt_compat import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, Qt, QIcon

from ..core.screensaver_manager import ScreensaverManager
from ..core.config_manager import ConfigManager

class MainWindow(QWidget):
    """Main application window providing a simplified interface"""
    
    def __init__(self, screensaver_manager: ScreensaverManager, config_manager: ConfigManager):
        super().__init__()
        self.screensaver_manager = screensaver_manager
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Restmode")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        self._setup_ui()
        self._setup_connections()
        self._update_status()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status Label
        self.status_label = QLabel("Screensaver Status: Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Toggle Button
        self.toggle_button = QPushButton("Activate Screensaver")
        self.toggle_button.setFixedSize(200, 40)
        self.toggle_button.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Settings Button
        settings_button = QPushButton("Open Settings")
        settings_button.setFixedSize(150, 30)
        settings_button.clicked.connect(self._open_settings)
        layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Hint Label
        self.hint_label = QLabel("Hint: Use Ctrl+Alt+S to toggle screensaver anytime.")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(self.hint_label)

        self.setLayout(layout)

    def _setup_connections(self):
        """Setup signal connections"""
        self.toggle_button.clicked.connect(self._on_toggle_button_clicked)
        self.screensaver_manager.screensaver_activated.connect(self._update_status)
        self.screensaver_manager.screensaver_deactivated.connect(self._update_status)
        
    def _update_status(self):
        """Update the status label and toggle button text"""
        if self.screensaver_manager.is_active:
            self.status_label.setText("Screensaver Status: <font color=\"green\">ACTIVE</font>")
            self.toggle_button.setText("Deactivate Screensaver")
            self.toggle_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #f44336; color: white;")
        else:
            self.status_label.setText("Screensaver Status: <font color=\"red\">INACTIVE</font>")
            self.toggle_button.setText("Activate Screensaver")
            self.toggle_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")

    def _on_toggle_button_clicked(self):
        """Handle toggle button click"""
        self.screensaver_manager.toggle_screensaver()

    def _open_settings(self):
        """Open the full settings dialog"""
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config_manager, parent=self)
        dialog.exec()

    def closeEvent(self, event):
        """Handle close event"""
        self.hide() # Hide instead of closing to allow background operation
        event.ignore() # Ignore close event to keep the app running in tray 