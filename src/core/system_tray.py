"""
System Tray Integration
Provides system tray menu and quick access functionality
"""

import logging
from src.utils.qt_compat import QSystemTrayIcon, QMenu, QAction, QMessageBox, QIcon, QPixmap, QPainter, QPen, QObject, pyqtSignal, Qt
from pathlib import Path

from .config_manager import ConfigManager
from .screensaver_manager import ScreensaverManager

class SystemTray(QObject):
    """System tray integration with menu and quick access"""
    
    # Signals
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    activate_requested = pyqtSignal()
    deactivate_requested = pyqtSignal()
    
    def __init__(self, screensaver_manager: ScreensaverManager, config_manager: ConfigManager, main_window: 'MainWindow'):
        super().__init__()
        self.screensaver_manager = screensaver_manager
        self.config_manager = config_manager
        self.main_window = main_window # Store reference to main window
        self.logger = logging.getLogger(__name__)
        
        # System tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("Restmode")
        
        # Setup
        self._setup_icon()
        self._setup_menu()
        self._setup_connections()
        
        # Show tray icon
        if self.config_manager.get('system.system_tray_enabled', True):
            self.tray_icon.show()
    
    def _setup_icon(self):
        """Setup system tray icon"""
        try:
            # Try to load custom icon
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.tray_icon.setIcon(QIcon(str(icon_path)))
            else:
                # Create a simple default icon
                self.logger.warning(f"Custom icon not found at {icon_path}. Creating default icon.")
                self._create_default_icon()
        except Exception as e:
            self.logger.error(f"Failed to setup tray icon: {e}")
            self._create_default_icon()
    
    def _create_default_icon(self):
        """Create a simple default icon"""
        try:
            # Create a simple 16x16 icon
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Draw a simple clock icon
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawEllipse(2, 2, 12, 12)
            painter.drawLine(8, 8, 8, 4)
            painter.drawLine(8, 8, 11, 8)
            painter.end()
            
            self.tray_icon.setIcon(QIcon(pixmap))
        except Exception as e:
            self.logger.error(f"Failed to create default icon: {e}")
    
    def _setup_menu(self):
        """Setup system tray menu"""
        try:
            menu = QMenu()
            
            # Status section
            status_action = QAction("Screensaver Status", self)
            status_action.setEnabled(False)
            menu.addAction(status_action)
            
            menu.addSeparator()
            
            # Control section
            activate_action = QAction("Activate Screensaver", self)
            activate_action.triggered.connect(self.activate_requested.emit)
            menu.addAction(activate_action)
            
            deactivate_action = QAction("Deactivate Screensaver", self)
            deactivate_action.triggered.connect(self.deactivate_requested.emit)
            menu.addAction(deactivate_action)
            
            menu.addSeparator()
            
            # Interface section
            self.show_interface_action = QAction("Show Interface", self)
            self.show_interface_action.triggered.connect(self._toggle_main_window_visibility)
            menu.addAction(self.show_interface_action)
            
            # Settings section
            settings_action = QAction("Settings", self)
            settings_action.triggered.connect(self.settings_requested.emit)
            menu.addAction(settings_action)
            
            # Dashboard section
            if self.config_manager.get('dashboard.enabled', False):
                dashboard_action = QAction("Dashboard", self)
                dashboard_action.triggered.connect(self._open_dashboard)
                menu.addAction(dashboard_action)
            
            menu.addSeparator()
            
            # System section
            startup_action = QAction("Start with Windows", self)
            startup_action.setCheckable(True)
            startup_action.setChecked(self.config_manager.get('system.startup_enabled', False))
            startup_action.triggered.connect(self._toggle_startup)
            menu.addAction(startup_action)
            
            menu.addSeparator()
            
            # About section
            about_action = QAction("About", self)
            about_action.triggered.connect(self._show_about)
            menu.addAction(about_action)
            
            # Quit section
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_requested.emit)
            menu.addAction(quit_action)
            
            # Store references for updates
            self.status_action = status_action
            self.activate_action = activate_action
            self.deactivate_action = deactivate_action
            self.startup_action = startup_action
            
            # Set menu
            self.tray_icon.setContextMenu(menu)
            
        except Exception as e:
            self.logger.error(f"Failed to setup tray menu: {e}")
    
    def _setup_connections(self):
        """Setup signal connections"""
        try:
            # Connect screensaver manager signals
            self.screensaver_manager.screensaver_activated.connect(self._on_screensaver_activated)
            self.screensaver_manager.screensaver_deactivated.connect(self._on_screensaver_deactivated)
            
            # Connect tray icon signals
            self.tray_icon.activated.connect(self._on_tray_activated)
            
        except Exception as e:
            self.logger.error(f"Failed to setup connections: {e}")
    
    def _on_screensaver_activated(self):
        """Handle screensaver activation"""
        try:
            self.status_action.setText("Status: Active")
            self.activate_action.setEnabled(False)
            self.deactivate_action.setEnabled(True)
            self.tray_icon.setToolTip("Restmode - Active")
        except Exception as e:
            self.logger.error(f"Error updating tray on activation: {e}")
    
    def _on_screensaver_deactivated(self):
        """Handle screensaver deactivation"""
        try:
            self.status_action.setText("Status: Inactive")
            self.activate_action.setEnabled(True)
            self.deactivate_action.setEnabled(False)
            self.tray_icon.setToolTip("Restmode - Inactive")
        except Exception as e:
            self.logger.error(f"Error updating tray on deactivation: {e}")
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        try:
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                # Double-click toggles screensaver
                if self.screensaver_manager.is_active:
                    self.deactivate_requested.emit()
                else:
                    self.activate_requested.emit()
        except Exception as e:
            self.logger.error(f"Error handling tray activation: {e}")
    
    def _open_dashboard(self):
        """Open dashboard in browser"""
        try:
            import webbrowser
            api_url = self.config_manager.get('dashboard.api_url', '')
            if api_url:
                dashboard_url = api_url.replace('/api/', '/dashboard/')
                webbrowser.open(dashboard_url)
            else:
                QMessageBox.warning(None, "Dashboard", "Dashboard URL not configured")
        except Exception as e:
            self.logger.error(f"Failed to open dashboard: {e}")
    
    def _toggle_startup(self, enabled: bool):
        """Toggle startup with Windows"""
        try:
            self.config_manager.set('system.startup_enabled', enabled)
            
            if enabled:
                self._enable_startup()
            else:
                self._disable_startup()
                
        except Exception as e:
            self.logger.error(f"Failed to toggle startup: {e}")
            QMessageBox.warning(None, "Startup", f"Failed to configure startup: {e}")
    
    def _enable_startup(self):
        """Enable startup with Windows"""
        try:
            import winreg
            
            # Get the path to the current executable
            import sys
            exe_path = sys.executable
            script_path = Path(__file__).parent.parent.parent / "main.py"
            
            # Create registry key
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
            
            # Set the value
            winreg.SetValueEx(
                key,
                "DesktopScreensaver",
                0,
                winreg.REG_SZ,
                f'"{exe_path}" "{script_path}"'
            )
            
            winreg.CloseKey(key)
            self.logger.info("Startup enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to enable startup: {e}")
            raise
    
    def _disable_startup(self):
        """Disable startup with Windows"""
        try:
            import winreg
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            
            # Delete the value
            try:
                winreg.DeleteValue(key, "DesktopScreensaver")
            except FileNotFoundError:
                pass  # Value doesn't exist
            
            winreg.CloseKey(key)
            self.logger.info("Startup disabled")
            
        except Exception as e:
            self.logger.error(f"Failed to disable startup: {e}")
            raise
    
    def _show_about(self):
        """Show about dialog"""
        try:
            QMessageBox.about(
                None,
                "About Desktop Screensaver",
                """
                <h3>Desktop Time & Date Screensaver</h3>
                <p>Version 1.0.0</p>
                <p>A professional Windows desktop application that displays a customizable full-screen time and date interface when the user is inactive.</p>
                <p><b>Features:</b></p>
                <ul>
                    <li>Smart inactivity detection</li>
                    <li>Customizable themes and display options</li>
                    <li>Dashboard integration</li>
                    <li>Multi-monitor support</li>
                    <li>Low resource usage</li>
                </ul>
                <p>Built with Python and PyQt6</p>
                """
            )
        except Exception as e:
            self.logger.error(f"Failed to show about dialog: {e}")
    
    def _toggle_main_window_visibility(self):
        """Toggle the visibility of the main application window (guest interface)"""
        try:
            if self.main_window:
                if self.main_window.isVisible():
                    self.main_window.hide()
                    self.show_interface_action.setText("Show Interface")
                else:
                    self.main_window.show()
                    self.main_window.activateWindow() # Bring to front
                    self.show_interface_action.setText("Hide Interface")
        except Exception as e:
            self.logger.error(f"Failed to toggle main window visibility: {e}")
    
    def show_notification(self, title: str, message: str, duration: int = 3000):
        """Show a system notification"""
        try:
            if self.tray_icon.isSystemTrayAvailable():
                self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration)
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
    
    def cleanup(self):
        """Cleanup system tray resources"""
        try:
            if self.tray_icon.isVisible():
                self.tray_icon.hide()
        except Exception as e:
            self.logger.error(f"Error during tray cleanup: {e}") 