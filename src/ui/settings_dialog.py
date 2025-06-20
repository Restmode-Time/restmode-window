"""
Settings Dialog
User-friendly configuration interface
"""

import logging
from src.utils.qt_compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, 
    QSpinBox, QComboBox, QCheckBox, QLineEdit, QPushButton, QGroupBox,
    QSlider, QFormLayout, QMessageBox, QFileDialog, Qt, pyqtSignal, QFont, QSizePolicy, QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Signal

from ..core.config_manager import ConfigManager
from .themes import get_themes
from .preview_widget import PreviewWidget

class SettingsDialog(QDialog):
    """Settings dialog for configuring the screensaver"""
    
    weather_test_result = Signal(str, bool)  # message, is_success
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Restmode Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Setup the user interface"""
        try:
            layout = QVBoxLayout()
            
            # Create tab widget
            tab_widget = QTabWidget()
            
            # General tab
            general_tab = self._create_general_tab()
            tab_widget.addTab(general_tab, "General")
            
            # Display tab
            display_tab = self._create_display_tab()
            tab_widget.addTab(display_tab, "Display")
            
            # To-Do List tab
            todo_tab = self._create_todo_tab()
            tab_widget.addTab(todo_tab, "To-Do List")
            
            # Weather tab
            weather_tab = self._create_weather_tab()
            tab_widget.addTab(weather_tab, "Weather")
            
            # System tab
            system_tab = self._create_system_tab()
            tab_widget.addTab(system_tab, "System")
            
            layout.addWidget(tab_widget)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            reset_button = QPushButton("Reset to Defaults")
            reset_button.clicked.connect(self._reset_to_defaults)
            button_layout.addWidget(reset_button)
            
            button_layout.addStretch()
            
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)
            
            save_button = QPushButton("Save")
            save_button.clicked.connect(self._save_settings)
            button_layout.addWidget(save_button)
            
            layout.addLayout(button_layout)
            
            self.setLayout(layout)
            
            self.weather_test_result.connect(self._show_weather_test_result)
            
        except Exception as e:
            self.logger.error(f"Failed to setup UI: {e}")
    
    def _create_general_tab(self):
        """Create general settings tab"""
        try:
            widget = QWidget()
            layout = QVBoxLayout()
            layout.setSpacing(20)

            # Activation settings
            activation_group = QGroupBox("Activation")
            activation_layout = QFormLayout()
            activation_layout.setVerticalSpacing(12)

            # Description label
            activation_desc = QLabel("Automatically activate the screensaver after a period of inactivity.")
            activation_desc.setStyleSheet("QLabel { color: gray; font-size: 11px; }")
            activation_layout.addRow(activation_desc)

            self.auto_activation_checkbox = QCheckBox("Enable automatic activation")
            self.auto_activation_checkbox.setToolTip("If checked, the screensaver will start automatically after a period of inactivity.")
            self.auto_activation_checkbox.stateChanged.connect(self._update_activation_controls)
            activation_layout.addRow("Auto Activation:", self.auto_activation_checkbox)

            # Delay spinbox and unit combo
            delay_layout = QHBoxLayout()
            self.delay_spinbox = QSpinBox()
            self.delay_spinbox.setRange(1, 3600)
            self.delay_spinbox.setToolTip("How long to wait before activating the screensaver.")
            delay_layout.addWidget(self.delay_spinbox)
            self.delay_unit_combo = QComboBox()
            self.delay_unit_combo.addItems(["minutes", "seconds"])
            self.delay_unit_combo.setCurrentText("minutes")
            self.delay_unit_combo.setToolTip("Choose the unit for the activation delay.")
            delay_layout.addWidget(self.delay_unit_combo)
            activation_layout.addRow("Activation Delay:", delay_layout)

            self.check_interval_spinbox = QSpinBox()
            self.check_interval_spinbox.setRange(1, 300)
            self.check_interval_spinbox.setSuffix(" seconds")
            self.check_interval_spinbox.setToolTip("How often to check for user inactivity (in seconds). Lower values are more responsive but use more resources.")
            activation_layout.addRow("Check Interval:", self.check_interval_spinbox)

            activation_group.setLayout(activation_layout)
            layout.addWidget(activation_group)

            # Hotkeys info
            hotkey_group = QGroupBox("Keyboard Shortcuts")
            hotkey_layout = QVBoxLayout()

            hotkey_info = QLabel(
                "Ctrl+Alt+S: Toggle screensaver\n"
                "Ctrl+Alt+Q: Emergency exit\n"
                "Any key/mouse: Deactivate screensaver"
            )
            hotkey_info.setStyleSheet("QLabel { color: gray; }")
            hotkey_layout.addWidget(hotkey_info)

            hotkey_group.setLayout(hotkey_layout)
            layout.addWidget(hotkey_group)

            layout.addStretch()
            widget.setLayout(layout)

            # Set initial enabled/disabled state
            self._update_activation_controls()
            return widget
        except Exception as e:
            self.logger.error(f"Failed to create general tab: {e}")
            return QWidget()
    
    def _update_activation_controls(self):
        """Enable/disable delay and interval controls based on auto activation checkbox."""
        enabled = self.auto_activation_checkbox.isChecked()
        self.delay_spinbox.setEnabled(enabled)
        self.check_interval_spinbox.setEnabled(enabled)
    
    def _create_display_tab(self):
        """Create display settings tab"""
        try:
            widget = QWidget()
            main_layout = QHBoxLayout() # Main horizontal layout for preview and controls

            # Left side: Settings controls
            settings_layout = QVBoxLayout()
            settings_layout.setSpacing(15) # Add some spacing between groups
            
            # Theme settings
            theme_group = QGroupBox("Theme")
            theme_layout = QFormLayout()
            
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(list(get_themes().keys()))
            self.theme_combo.currentIndexChanged.connect(self._update_preview_from_ui)
            theme_layout.addRow("Theme:", self.theme_combo)
            
            self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
            self.opacity_slider.setRange(50, 100)
            self.opacity_slider.valueChanged.connect(self._update_preview_from_ui)
            theme_layout.addRow("Opacity:", self.opacity_slider)
            
            theme_group.setLayout(theme_layout)
            settings_layout.addWidget(theme_group)
            
            # Time settings
            time_group = QGroupBox("Time Display")
            time_layout = QFormLayout()
            
            self.time_format_combo = QComboBox()
            self.time_format_combo.addItems(['12h', '24h'])
            self.time_format_combo.currentIndexChanged.connect(self._update_preview_from_ui)
            time_layout.addRow("Time Format:", self.time_format_combo)
            
            self.show_seconds_checkbox = QCheckBox("Show seconds")
            self.show_seconds_checkbox.stateChanged.connect(self._update_preview_from_ui)
            time_layout.addRow("Seconds:", self.show_seconds_checkbox)
            
            self.font_size_spinbox = QSpinBox()
            self.font_size_spinbox.setRange(24, 120)
            self.font_size_spinbox.setSuffix(" px")
            self.font_size_spinbox.valueChanged.connect(self._update_preview_from_ui)
            time_layout.addRow("Font Size:", self.font_size_spinbox)

            self.font_family_combo = QComboBox()
            self.font_family_combo.addItems(["Segoe UI", "Arial", "Verdana", "Times New Roman", "Courier New", "Georgia", "Palatino Linotype"])
            self.font_family_combo.currentIndexChanged.connect(self._update_preview_from_ui)
            time_layout.addRow("Font Family:", self.font_family_combo)

            self.font_style_combo = QComboBox()
            self.font_style_combo.addItems(["normal", "italic"])
            self.font_style_combo.currentIndexChanged.connect(self._update_preview_from_ui)
            time_layout.addRow("Font Style:", self.font_style_combo)
            
            time_group.setLayout(time_layout)
            settings_layout.addWidget(time_group)
            
            # Date settings
            date_group = QGroupBox("Date Display")
            date_layout = QFormLayout()
            
            self.show_date_checkbox = QCheckBox("Show date")
            self.show_date_checkbox.stateChanged.connect(self._update_preview_from_ui)
            date_layout.addRow("Show Date:", self.show_date_checkbox)
            
            self.date_format_combo = QComboBox()
            self.date_format_combo.addItems(['full', 'short', 'iso'])
            self.date_format_combo.currentIndexChanged.connect(self._update_preview_from_ui)
            date_layout.addRow("Date Format:", self.date_format_combo)
            
            date_group.setLayout(date_layout)
            settings_layout.addWidget(date_group)
            
            settings_layout.addStretch()

            # Right side: Monitor-style Preview Widget
            preview_container = QVBoxLayout()
            monitor_frame = QFrame()
            monitor_frame.setObjectName("MonitorFrame")
            monitor_frame.setStyleSheet("""
                QFrame#MonitorFrame {
                    border: 6px solid #222;
                    border-radius: 24px;
                    background: #111;
                }
            """)
            monitor_layout = QVBoxLayout(monitor_frame)
            monitor_layout.setContentsMargins(18, 18, 18, 18)
            self.preview_widget = PreviewWidget(self.config_manager)
            self.preview_widget.setMinimumSize(350, 250)
            self.preview_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            monitor_layout.addWidget(self.preview_widget)
            # Optional: Add a "stand" below the monitor
            stand = QFrame()
            stand.setFixedSize(60, 16)
            stand.setStyleSheet("border-radius: 8px; background: #333;")
            preview_container.addWidget(monitor_frame, alignment=Qt.AlignmentFlag.AlignCenter)
            preview_container.addWidget(stand, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            preview_container.addStretch()

            # Add both layouts to the main horizontal layout
            main_layout.addLayout(settings_layout, 1)
            main_layout.addLayout(preview_container, 1)
            widget.setLayout(main_layout)
            return widget
            
        except Exception as e:
            self.logger.error(f"Failed to create display tab: {e}")
            return QWidget()
    
    def _create_weather_tab(self):
        """Create weather settings tab"""
        try:
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Weather settings
            weather_group = QGroupBox("Weather Display")
            weather_layout = QFormLayout()
            
            self.show_weather_checkbox = QCheckBox("Show weather information")
            weather_layout.addRow("Enable Weather:", self.show_weather_checkbox)
            
            self.weather_location_edit = QLineEdit()
            self.weather_location_edit.setPlaceholderText("City, Country (e.g., London, UK)")
            # Pre-fill with default if not set, using IP geolocation
            if not self.config_manager.get('weather.location', '').strip():
                try:
                    import requests
                    resp = requests.get('http://ip-api.com/json/', timeout=3)
                    if resp.status_code == 200:
                        data = resp.json()
                        city = data.get('city', '')
                        country = data.get('countryCode', '')
                        if city and country:
                            self.weather_location_edit.setText(f'{city}, {country}')
                        else:
                            raise Exception('No city/country from IP')
                    else:
                        raise Exception('IP API failed')
                except Exception:
                    from PySide6.QtWidgets import QInputDialog
                    pin, ok = QInputDialog.getText(self, 'Enter PIN Code', 'Could not detect your location.\nPlease enter your PIN code (postal code) for local weather:')
                    if ok and pin.strip():
                        self.weather_location_edit.setText(pin.strip())
                    else:
                        self.weather_location_edit.setText('')
            weather_layout.addRow("Location:", self.weather_location_edit)
            
            self.weather_units_combo = QComboBox()
            self.weather_units_combo.addItems(['metric', 'imperial'])
            weather_layout.addRow("Units:", self.weather_units_combo)
            
            weather_group.setLayout(weather_layout)
            layout.addWidget(weather_group)
            
            # Test weather button
            test_weather_button = QPushButton("Test Weather")
            test_weather_button.clicked.connect(self._test_weather)
            layout.addWidget(test_weather_button)
            
            layout.addStretch()
            widget.setLayout(layout)
            return widget
            
        except Exception as e:
            self.logger.error(f"Failed to create weather tab: {e}")
            return QWidget()
    
    def _create_system_tab(self):
        """Create system settings tab"""
        try:
            widget = QWidget()
            layout = QVBoxLayout()
            
            # System settings
            system_group = QGroupBox("System")
            system_layout = QFormLayout()
            
            self.startup_checkbox = QCheckBox("Start with Windows")
            system_layout.addRow("Startup:", self.startup_checkbox)
            
            self.system_tray_checkbox = QCheckBox("Show in system tray")
            system_layout.addRow("System Tray:", self.system_tray_checkbox)
            
            self.multi_monitor_checkbox = QCheckBox("Support multiple monitors")
            system_layout.addRow("Multi Monitor:", self.multi_monitor_checkbox)
            
            self.low_power_checkbox = QCheckBox("Low power mode")
            system_layout.addRow("Low Power:", self.low_power_checkbox)

            self.turn_off_screen_delay_spinbox = QSpinBox()
            self.turn_off_screen_delay_spinbox.setRange(0, 240) # 0 for disable, up to 4 hours
            self.turn_off_screen_delay_spinbox.setSuffix(" minutes (0 to disable)")
            system_layout.addRow("Turn off screen after:", self.turn_off_screen_delay_spinbox)
            
            system_group.setLayout(system_layout)
            layout.addWidget(system_group)
            
            # Import/Export
            import_export_group = QGroupBox("Configuration")
            import_export_layout = QHBoxLayout()
            
            export_button = QPushButton("Export Settings")
            export_button.clicked.connect(self._export_settings)
            import_export_layout.addWidget(export_button)
            
            import_button = QPushButton("Import Settings")
            import_button.clicked.connect(self._import_settings)
            import_export_layout.addWidget(import_button)
            
            import_export_group.setLayout(import_export_layout)
            layout.addWidget(import_export_group)
            
            layout.addStretch()
            widget.setLayout(layout)
            return widget
            
        except Exception as e:
            self.logger.error(f"Failed to create system tab: {e}")
            return QWidget()
    
    def _create_todo_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        # Enable To-Do overlay checkbox
        self.show_todo_checkbox = QCheckBox("Show To-Do List in Screensaver")
        layout.addWidget(self.show_todo_checkbox)
        # Get accent color from current theme
        theme_name = self.config_manager.get('display.theme', 'dark')
        theme = get_themes().get(theme_name, get_themes()['dark'])
        accent = theme['accent'].name() if hasattr(theme['accent'], 'name') else str(theme['accent'])
        # Glassy card frame
        card = QFrame()
        card.setObjectName("TodoCard")
        card.setStyleSheet(f"""
            QFrame#TodoCard {{
                background: #181a20;
                border-radius: 16px;
                border: 1.5px solid #333;
            }}
            QListWidget {{
                background: transparent;
                color: #fff;
                font-size: 16px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 6px;
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background: #222;
                color: #00eaff;
            }}
            QLineEdit {{
                background: #23242a;
                border: 1.2px solid #333;
                border-radius: 8px;
                color: #fff;
                font-size: 15px;
                padding: 6px 10px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton {{
                background: #23242a;
                color: #fff;
                border: 1.2px solid #333;
                border-radius: 8px;
                font-size: 15px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                padding: 7px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #222;
                color: #00eaff;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)
        title = QLabel("To-Do List")
        title.setStyleSheet(f"font-weight: bold; color: #fff; font-size: 22px; letter-spacing: 1.5px;")
        card_layout.addWidget(title)
        self.todo_list = QListWidget()
        card_layout.addWidget(self.todo_list)
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Add a new to-do item...")
        input_layout.addWidget(self.todo_input)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_todo_item)
        input_layout.addWidget(add_btn)
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self._preview_todo_in_monitor)
        input_layout.addWidget(preview_btn)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_selected_todo)
        input_layout.addWidget(remove_btn)
        card_layout.addLayout(input_layout)
        layout.addWidget(card)
        widget.setLayout(layout)
        return widget

    def _add_todo_item(self):
        text = self.todo_input.text().strip()
        if text:
            self.todo_list.addItem(text)
            self.todo_input.clear()
        else:
            QMessageBox.warning(self, "Empty To-Do", "Please enter a to-do item.")

    def _remove_selected_todo(self):
        for item in self.todo_list.selectedItems():
            self.todo_list.takeItem(self.todo_list.row(item))

    def _preview_todo_in_monitor(self):
        # Update the preview monitor with the current to-do items and display settings
        settings = {
            'todo_items': [self.todo_list.item(i).text() for i in range(self.todo_list.count())],
            'theme': self.theme_combo.currentText(),
            'opacity': self.opacity_slider.value() / 100.0,
            'time_format': self.time_format_combo.currentText(),
            'show_seconds': self.show_seconds_checkbox.isChecked(),
            'font_size': self.font_size_spinbox.value(),
            'font_family': self.font_family_combo.currentText(),
            'font_style': self.font_style_combo.currentText(),
            'show_date': self.show_date_checkbox.isChecked(),
            'date_format': self.date_format_combo.currentText(),
        }
        if hasattr(self, 'preview_widget'):
            self.preview_widget.update_from_settings(settings)

    def _load_current_settings(self):
        """Load current settings into the UI"""
        try:
            # General settings
            self.auto_activation_checkbox.setChecked(
                self.config_manager.get('activation.enable_auto_activation', True)
            )
            delay_value = self.config_manager.get('activation.delay_value', 5)
            delay_unit = self.config_manager.get('activation.delay_unit', 'minutes')
            self.delay_spinbox.setValue(delay_value)
            self.delay_unit_combo.setCurrentText(delay_unit)
            self.check_interval_spinbox.setValue(
                self.config_manager.get('activation.check_interval_seconds', 30)
            )
            
            # Display settings
            theme = self.config_manager.get('display.theme', 'dark')
            index = self.theme_combo.findText(theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
            
            opacity = int(self.config_manager.get('display.opacity', 0.9) * 100)
            self.opacity_slider.setValue(opacity)
            
            time_format = self.config_manager.get('display.time_format', '24h')
            index = self.time_format_combo.findText(time_format)
            if index >= 0:
                self.time_format_combo.setCurrentIndex(index)
            
            self.show_seconds_checkbox.setChecked(
                self.config_manager.get('display.show_seconds', True)
            )
            self.font_size_spinbox.setValue(
                self.config_manager.get('display.font_size', 72)
            )
            self.show_date_checkbox.setChecked(
                self.config_manager.get('display.show_date', True)
            )
            
            date_format = self.config_manager.get('display.date_format', 'full')
            index = self.date_format_combo.findText(date_format)
            if index >= 0:
                self.date_format_combo.setCurrentIndex(index)
            
            # Font settings
            self.font_family_combo.setCurrentText(
                self.config_manager.get('display.font_family', 'Segoe UI')
            )
            self.font_style_combo.setCurrentText(
                self.config_manager.get('display.font_style', 'normal')
            )

            # System settings
            self.startup_checkbox.setChecked(
                self.config_manager.get('system.startup_enabled', False)
            )
            self.system_tray_checkbox.setChecked(
                self.config_manager.get('system.system_tray_enabled', True)
            )
            self.multi_monitor_checkbox.setChecked(
                self.config_manager.get('system.multi_monitor', True)
            )
            self.low_power_checkbox.setChecked(
                self.config_manager.get('system.low_power_mode', True)
            )
            self.turn_off_screen_delay_spinbox.setValue(
                self.config_manager.get('system.turn_off_screen_delay_minutes', 0)
            )
            
            # Load to-do list
            self.todo_list.clear()
            todos = self.config_manager.get('todo.items', [])
            for todo in todos:
                self.todo_list.addItem(todo)
            
            # To-Do overlay enable
            self.show_todo_checkbox.setChecked(self.config_manager.get('display.show_todo', True))
            
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
    
    def _save_settings(self):
        """Save settings from UI to configuration"""
        try:
            # General settings
            self.config_manager.set('activation.enable_auto_activation', 
                                   self.auto_activation_checkbox.isChecked())
            self.config_manager.set('activation.delay_value', 
                                   self.delay_spinbox.value())
            self.config_manager.set('activation.delay_unit', 
                                   self.delay_unit_combo.currentText())
            self.config_manager.set('activation.check_interval_seconds', 
                                   self.check_interval_spinbox.value())
            
            # Display settings
            self.config_manager.set('display.theme', self.theme_combo.currentText())
            self.config_manager.set('display.opacity', self.opacity_slider.value() / 100)
            self.config_manager.set('display.time_format', self.time_format_combo.currentText())
            self.config_manager.set('display.show_seconds', self.show_seconds_checkbox.isChecked())
            self.config_manager.set('display.font_size', self.font_size_spinbox.value())
            self.config_manager.set('display.show_date', self.show_date_checkbox.isChecked())
            self.config_manager.set('display.date_format', self.date_format_combo.currentText())
            
            # Font settings
            self.config_manager.set(
                'display.font_family', self.font_family_combo.currentText()
            )
            self.config_manager.set(
                'display.font_style', self.font_style_combo.currentText()
            )

            # System settings
            self.config_manager.set('system.startup_enabled', self.startup_checkbox.isChecked())
            self.config_manager.set('system.system_tray_enabled', self.system_tray_checkbox.isChecked())
            self.config_manager.set('system.multi_monitor', self.multi_monitor_checkbox.isChecked())
            self.config_manager.set('system.low_power_mode', self.low_power_checkbox.isChecked())
            self.config_manager.set('system.turn_off_screen_delay_minutes', self.turn_off_screen_delay_spinbox.value())
            
            # Save to-do list
            todos = [self.todo_list.item(i).text() for i in range(self.todo_list.count())]
            print(f"[DEBUG] Saving to-do items to config: {todos}")
            self.config_manager.set('todo.items', todos)
            # Emit config_updated signal if available
            if hasattr(self.config_manager, 'config_updated'):
                self.config_manager.config_updated.emit(self.config_manager.config)
            
            # To-Do overlay enable
            self.config_manager.set('display.show_todo', self.show_todo_checkbox.isChecked())
            
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        try:
            reply = QMessageBox.question(
                self, "Reset Settings",
                "Are you sure you want to reset all settings to defaults?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.config_manager.reset_to_defaults()
                self._load_current_settings()
                QMessageBox.information(self, "Settings", "Settings reset to defaults!")
                
        except Exception as e:
            self.logger.error(f"Failed to reset settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to reset settings: {e}")
    
    def _test_weather(self):
        """Test weather connection using WeatherAPI.com in a background thread and update UI via signal."""
        try:
            import threading, requests
            location = self.weather_location_edit.text().strip()
            if not location:
                self.weather_test_result.emit("Please enter your location (city, country or PIN code).", False)
                return
            api_key = '8aa65584f01d432f9f5133344251906'
            def fetch_weather():
                try:
                    url = 'http://api.weatherapi.com/v1/current.json'
                    params = {'key': api_key, 'q': location, 'aqi': 'no'}
                    resp = requests.get(url, params=params, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        current = data.get('current', {})
                        cond = current.get('condition', {})
                        temp_c = current.get('temp_c')
                        text = cond.get('text', '')
                        msg = f"Weather for {location}:\n{text}, {temp_c}°C"
                        self.weather_test_result.emit(msg, True)
                    else:
                        self.weather_test_result.emit(f"Failed to fetch weather. Status: {resp.status_code}\n{resp.text}", False)
                except Exception as e:
                    self.weather_test_result.emit(f"Failed to fetch weather: {e}", False)
            threading.Thread(target=fetch_weather, daemon=True).start()
        except Exception as e:
            self.logger.error(f"Failed to test weather: {e}")
    
    def _show_weather_test_result(self, message, is_success):
        from PySide6.QtWidgets import QMessageBox
        if is_success:
            QMessageBox.information(self, "Weather", message)
        else:
            QMessageBox.critical(self, "Weather", message)
    
    def _export_settings(self):
        """Export settings to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Settings", "", "JSON Files (*.json)"
            )
            if file_path:
                self.config_manager.export_config(file_path)
                QMessageBox.information(self, "Export", "Settings exported successfully!")
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import settings from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Settings", "", "JSON Files (*.json)"
            )
            if file_path:
                self.config_manager.import_config(file_path)
                self._load_current_settings()
                QMessageBox.information(self, "Import", "Settings imported successfully!")
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to import settings: {e}")
    
    def _update_preview_from_ui(self):
        """Update the preview widget live as settings are changed"""
        settings = {
            'theme': self.theme_combo.currentText(),
            'opacity': self.opacity_slider.value() / 100.0,
            'time_format': self.time_format_combo.currentText(),
            'show_seconds': self.show_seconds_checkbox.isChecked(),
            'font_size': self.font_size_spinbox.value(),
            'font_family': self.font_family_combo.currentText(),
            'font_style': self.font_style_combo.currentText(),
            'show_date': self.show_date_checkbox.isChecked(),
            'date_format': self.date_format_combo.currentText(),
        }
        self.preview_widget.update_from_settings(settings)
    
    def _update_activation_controls(self):
        """Enable/disable delay and interval controls based on auto activation checkbox."""
        enabled = self.auto_activation_checkbox.isChecked()
        self.delay_spinbox.setEnabled(enabled)
        self.check_interval_spinbox.setEnabled(enabled) 