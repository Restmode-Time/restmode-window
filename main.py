#!/usr/bin/env python3
"""
Desktop Time & Date Screensaver
Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Qt classes from compatibility layer
from src.utils.qt_compat import QApplication, QTimer, QThread, QIcon

from src.core.screensaver_manager import ScreensaverManager
from src.core.system_tray import SystemTray
from src.core.config_manager import ConfigManager
from src.utils.logger import setup_logging
from src.utils.error_handler import ErrorHandler
from src.ui.main_window import MainWindow

class ScreensaverApp:
    """Main application class for the screensaver"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Restmode")
        self.app.setApplicationVersion("1.0.0")
        self.app.setQuitOnLastWindowClosed(False)
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Setup error handling
        self.error_handler = ErrorHandler()
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        
        # Initialize core components
        self.screensaver_manager = None
        self.system_tray = None
        self.main_window = None
        
        # Setup application icon
        self._setup_icon()
        
    def _setup_icon(self):
        """Setup application icon"""
        try:
            import sys, os
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.app.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            self.logger.warning(f"Could not load application icon: {e}")
    
    def initialize(self):
        """Initialize all application components"""
        try:
            self.logger.info("Initializing Desktop Screensaver application...")
            
            # Initialize screensaver manager
            self.screensaver_manager = ScreensaverManager(self.config_manager)
            
            # Initialize main window (guest interface)
            self.main_window = MainWindow(self.screensaver_manager, self.config_manager)
            self.main_window.show()

            # Initialize system tray
            self.system_tray = SystemTray(self.screensaver_manager, self.config_manager, self.main_window)
            
            # Connect signals
            self._connect_signals()
            
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(f"Failed to initialize application: {e}")
            return False
    
    def _connect_signals(self):
        """Connect application signals"""
        try:
            # Connect system tray signals
            self.system_tray.quit_requested.connect(self.quit_application)
            self.system_tray.settings_requested.connect(self.show_settings)
            
            # Connect screensaver manager signals
            self.screensaver_manager.error_occurred.connect(
                lambda error: self.error_handler.handle_error(error)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to connect signals: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            from src.ui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self.config_manager, parent=None)
            dialog.exec()
        except Exception as e:
            self.error_handler.handle_error(f"Failed to show settings: {e}")
    
    def run(self):
        """Run the application"""
        try:
            if not self.initialize():
                return 1
            
            self.logger.info("Starting application...")
            
            # Start the event loop
            return self.app.exec()
            
        except Exception as e:
            self.error_handler.handle_error(f"Application failed to run: {e}")
            return 1
    
    def quit_application(self):
        """Cleanly quit the application"""
        try:
            self.logger.info("Quitting application...")
            
            # Cleanup resources
            if self.screensaver_manager:
                self.screensaver_manager.cleanup()
            
            if self.system_tray:
                self.system_tray.cleanup()
            
            self.app.quit()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            self.app.quit()

def main():
    """Main entry point"""
    try:
        app = ScreensaverApp()
        return app.run()
    except Exception as e:
        print(f"Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 