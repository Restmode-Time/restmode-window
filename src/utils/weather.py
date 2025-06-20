"""
Weather Widget
Displays weather information in the screensaver
"""

import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from src.utils.qt_compat import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTimer, pyqtSignal, QFont, Qt
from src.utils.worker_thread import WorkerThread

from ..core.config_manager import ConfigManager

class WeatherWidget(QWidget):
    """Widget for displaying weather information"""
    
    weather_update_completed = pyqtSignal(bool)

    def __init__(self, config_manager: ConfigManager, is_preview_mode: bool = False):
        super().__init__()
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.is_preview_mode = is_preview_mode # New flag for preview mode
        
        # Weather data
        self.weather_data = None
        self.last_update = None
        self.weather_fetch_thread = None
        
        # Setup UI
        self._setup_ui()
        
        # Setup update timer - only run in non-preview mode
        if not self.is_preview_mode:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.start_weather_fetch)
            self.update_timer.start(30 * 60 * 1000)  # Update every 30 minutes
            
            # Initial update for non-preview mode
            self.start_weather_fetch()
        else:
            # For preview mode, we only update when explicitly called by update_weather() in PreviewWidget
            self._show_no_weather()
    
    def _setup_ui(self):
        """Setup the user interface"""
        try:
            layout = QVBoxLayout()
            
            if self.is_preview_mode:
                layout.setContentsMargins(5, 0, 5, 0) # Smaller margins for preview
                layout.setSpacing(2) # Smaller spacing for preview
            else:
                layout.setContentsMargins(20, 10, 20, 10)
                layout.setSpacing(5)
            
            # Weather icon and temperature
            temp_layout = QHBoxLayout()
            
            self.weather_icon_label = QLabel()
            # Adjust icon size for preview mode
            icon_size = 20 if self.is_preview_mode else 32
            self.weather_icon_label.setFixedSize(icon_size, icon_size)
            temp_layout.addWidget(self.weather_icon_label)
            
            self.temperature_label = QLabel()
            self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            temp_layout.addWidget(self.temperature_label)
            
            temp_layout.addStretch()
            layout.addLayout(temp_layout)
            
            # Weather description
            self.description_label = QLabel()
            self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.description_label)
            
            # Location and time
            self.location_label = QLabel()
            self.location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.location_label)
            
            self.setLayout(layout)
            
            # Apply styling
            self._apply_styling()
            
        except Exception as e:
            self.logger.error(f"Failed to setup weather UI: {e}")
    
    def _apply_styling(self):
        """Apply styling to the weather widget"""
        try:
            # Get current theme colors
            theme_name = self.config_manager.get('display.theme', 'dark')
            if theme_name == 'light':
                text_color = "#1e1e1e"
                accent_color = "#0078d4"
            else:
                text_color = "#ffffff"
                accent_color = "#00b4ff"
            
            # Determine font sizes based on preview mode
            base_font_size = 10 if self.is_preview_mode else 14
            temp_font_size = 14 if self.is_preview_mode else 18

            # Apply styles
            self.setStyleSheet(f"""
                QWidget {{
                    background: transparent;
                    color: {text_color};
                }}
                QLabel {{
                    background: transparent;
                    color: {text_color};
                    font-size: {base_font_size}px;
                }}
            """)
            
            # Temperature label styling
            self.temperature_label.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    color: {accent_color};
                    font-size: {temp_font_size}px;
                    font-weight: bold;
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to apply weather styling: {e}")
    
    def start_weather_fetch(self):
        """Initiate weather data fetching in a worker thread."""
        if not self.config_manager.get('display.show_weather', False):
            self.hide()
            return
        # Use built-in WeatherAPI.com key
        api_key = '8aa65584f01d432f9f5133344251906'
        location = self.config_manager.get('weather.location', '')
        if not location:
            self._show_no_weather()
            return
        self.logger.info("Starting weather data fetch in background thread.")
        self.weather_fetch_thread = WorkerThread(self._perform_weather_fetch_task, api_key, location)
        self.weather_fetch_thread.signals.result.connect(self._on_weather_fetch_success)
        self.weather_fetch_thread.signals.error.connect(self._on_weather_fetch_error)
        self.weather_fetch_thread.start()

    def _perform_weather_fetch_task(self, api_key: str, location: str) -> Optional[Dict[str, Any]]:
        """Performs the actual weather data fetching (blocking network request) using WeatherAPI.com."""
        base_url = "http://api.weatherapi.com/v1/current.json"
        params = {
            'key': api_key,
            'q': location,
            'aqi': 'no'
        }
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        self.logger.info(f"Weather data fetched for {location}")
        return data

    def _on_weather_fetch_success(self, weather_data: Dict[str, Any]):
        """Handle successful weather data fetch result."""
        if weather_data:
            self._display_weather(weather_data)
            self.weather_update_completed.emit(True)
        else:
            self._show_no_weather()
            self.weather_update_completed.emit(False)

    def _on_weather_fetch_error(self, error_message: str, traceback_str: str):
        """Handle errors during weather data fetch."""
        self.logger.error(f"Weather data fetch error: {error_message}\n{traceback_str}")
        self._show_no_weather()
        self.weather_update_completed.emit(False)

    def update_weather(self):
        self.logger.warning("This method is deprecated and should not be called directly. Use start_weather_fetch instead.")
        # In preview mode, allow direct update without re-fetching via thread
        if self.is_preview_mode:
            self.start_weather_fetch()
        else:
            self.start_weather_fetch()

    def _fetch_weather(self, api_key: str, location: str, units: str) -> Optional[Dict[str, Any]]:
        self.logger.warning("This method is deprecated and should not be called directly. It's now part of the worker thread.")
        return None # This method is now handled by _perform_weather_fetch_task in WorkerThread

    def _display_weather(self, weather_data: Dict[str, Any]):
        """Display weather information from WeatherAPI.com response."""
        try:
            # Extract weather information
            current = weather_data.get('current', {})
            location = weather_data.get('location', {})
            temp_c = current.get('temp_c')
            temp_f = current.get('temp_f')
            condition = current.get('condition', {})
            icon_url = condition.get('icon', '')
            text = condition.get('text', '')
            city = location.get('name', '')
            country = location.get('country', '')
            # Set icon
            if icon_url:
                from PySide6.QtGui import QPixmap
                import requests
                try:
                    icon_data = requests.get(f"http:{icon_url}" if icon_url.startswith('//') else icon_url, timeout=5).content
                    pixmap = QPixmap()
                    pixmap.loadFromData(icon_data)
                    self.weather_icon_label.setPixmap(pixmap.scaled(self.weather_icon_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                except Exception:
                    self.weather_icon_label.clear()
            else:
                self.weather_icon_label.clear()
            # Set temperature
            if temp_c is not None:
                self.temperature_label.setText(f"{temp_c:.1f}°C")
            elif temp_f is not None:
                self.temperature_label.setText(f"{temp_f:.1f}°F")
            else:
                self.temperature_label.setText("")
            # Set description
            self.description_label.setText(text)
            # Set location
            self.location_label.setText(f"{city}, {country}")
            self.show()
        except Exception as e:
            self.logger.error(f"Failed to display weather: {e}")
            self._show_no_weather()
    
    def _set_weather_icon(self, icon_code: str):
        """Set weather icon based on icon code"""
        try:
            # Map icon codes to emoji
            icon_map = {
                '01d': '☀️',  # clear sky day
                '01n': '🌙',  # clear sky night
                '02d': '⛅',  # few clouds day
                '02n': '☁️',  # few clouds night
                '03d': '☁️',  # scattered clouds
                '03n': '☁️',  # scattered clouds
                '04d': '☁️',  # broken clouds
                '04n': '☁️',  # broken clouds
                '09d': '🌧️',  # shower rain
                '09n': '🌧️',  # shower rain
                '10d': '🌦️',  # rain day
                '10n': '🌧️',  # rain night
                '11d': '⛈️',  # thunderstorm
                '11n': '⛈️',  # thunderstorm
                '13d': '🌨️',  # snow
                '13n': '🌨️',  # snow
                '50d': '🌫️',  # mist
                '50n': '🌫️',  # mist
            }
            
            emoji = icon_map.get(icon_code, '🌤️')
            self.weather_icon_label.setText(emoji)
            
        except Exception as e:
            self.logger.error(f"Failed to set weather icon: {e}")
            self.weather_icon_label.setText('🌤️')
    
    def _show_no_weather(self):
        """Show no weather information"""
        try:
            self.temperature_label.setText("--")
            self.description_label.setText("Weather unavailable")
            self.location_label.setText("")
            self.weather_icon_label.setText("🌤️")
            self.show()
        except Exception as e:
            self.logger.error(f"Failed to show no weather: {e}")
    
    def get_weather_summary(self) -> str:
        """Get a summary of current weather"""
        try:
            if not self.weather_data:
                return "Weather unavailable"
            
            main = self.weather_data.get('main', {})
            weather = self.weather_data.get('weather', [{}])[0]
            
            temp = main.get('temp', 0)
            temp_unit = '°C' if self.config_manager.get('weather.units', 'metric') == 'metric' else '°F'
            description = weather.get('description', '').title()
            
            return f"{temp:.1f}{temp_unit}, {description}"
            
        except Exception as e:
            self.logger.error(f"Failed to get weather summary: {e}")
            return "Weather unavailable" 