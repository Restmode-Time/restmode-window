"""
Screensaver Window
Beautiful full-screen time and date display with themes
"""

import logging
import random
from datetime import datetime
from typing import Dict, Any
from src.utils.qt_compat import QWidget, QVBoxLayout, QHBoxLayout, QLabel, Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QFont, QPalette, QLinearGradient, QPixmap, QScreen, QPoint, QFrame
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QFont

from ..core.config_manager import ConfigManager
from ..utils.weather import WeatherWidget
from .themes import get_themes

class ScreensaverWindow(QWidget):
    """Full-screen screensaver window with time and date display"""
    
    # Signals
    closed = pyqtSignal()
    
    def __init__(self, screen, config_manager: ConfigManager):
        super().__init__()
        self.screen = screen
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        print(f"[DEBUG] ScreensaverWindow config_manager id: {id(self.config_manager)}")
        
        # Emoji elements
        self.emoji_label = None
        self.emoji_animation = None
        
        # Cache config values at startup
        self._cached_config = dict(self.config_manager.config) if hasattr(self.config_manager, 'config') else {}
        
        # Setup window
        self._setup_window()
        self.themes = get_themes()
        self._setup_ui()
        self._setup_animations()
        
        # Start update timer
        self.update_timer = QTimer()
        low_power = self.config_manager.get('system.low_power_mode', True)
        if low_power:
            self.update_timer.timeout.connect(self._update_display)
            self.update_timer.start(5000)  # Update every 5 seconds in low power mode
            self._stop_emoji_animation()  # Stop animations in low power mode
        else:
            self.update_timer.timeout.connect(self._update_display)
            self.update_timer.start(1000)  # Update every second
        
        # Lazy load weather widget after window is shown
        QTimer.singleShot(200, self._lazy_load_weather)
        
        # Connect to config_updated signal
        if hasattr(self.config_manager, 'config_updated'):
            self.config_manager.config_updated.connect(self._on_config_updated)
        
        # Initial update
        self._update_display()
    
    def _setup_window(self):
        """Setup window properties"""
        try:
            # Set window flags for full-screen screensaver
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
            
            # Set window state
            self.setWindowState(Qt.WindowState.WindowFullScreen)
            
            # Position window on the correct screen
            geometry = self.screen.geometry()
            self.setGeometry(geometry)
            
            # Set window title
            self.setWindowTitle("Desktop Screensaver")
            
        except Exception as e:
            self.logger.error(f"Failed to setup window: {e}")
    
    def _setup_ui(self):
        """Setup user interface"""
        try:
            # Main layout
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Time display
            self.time_label = QLabel("12:34:56 PM")
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.time_label.setStyleSheet("color: white; font-size: 80px; background: transparent;")
            layout.addWidget(self.time_label, stretch=2)
            
            # Weather label (directly under time)
            self.weather_label = QLabel("")
            self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_label.setStyleSheet("color: #b3e6ff; font-size: 32px; font-weight: bold; background: transparent; margin-bottom: 12px;")
            layout.addWidget(self.weather_label, stretch=0)
            
            # Date display
            self.date_label = QLabel("01/01/2025")
            self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.date_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.date_label.setStyleSheet("color: #eee; font-size: 36px; background: transparent;")
            layout.addWidget(self.date_label, stretch=1)
            
            # Weather widget placeholder (lazy loaded)
            self.weather_widget = None
            
            # To-Do Glass Card Overlay (bottom right)
            self.todo_card = QFrame(self)
            self.todo_card.setObjectName("TodoGlassCard")
            self.todo_card.setStyleSheet("""
                QFrame#TodoGlassCard {
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(30,30,40,0.85),
                        stop:1 rgba(30,30,40,0.65)
                    );
                    border-radius: 28px;
                }
            """)
            self.todo_card.setFixedWidth(340)
            self.todo_card_layout = QVBoxLayout(self.todo_card)
            self.todo_card_layout.setContentsMargins(22, 18, 22, 18)
            self.todo_card_title = QLabel("To-Do List")
            self.todo_card_title.setStyleSheet(
                "font-weight: bold; color: #fff; font-size: 22px; letter-spacing: 2px; "
                "text-shadow: 1px 1px 8px #00eaff;"
            )
            self.todo_card_title.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
            self.todo_card_layout.addWidget(self.todo_card_title)
            self.todo_card_labels = []
            self.todo_card.hide()
            
            # Animated Emoji Label (positioned absolutely)
            self.emoji_label = QLabel(self)
            self.emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.emoji_label.hide()

            # Set layout
            self.setLayout(layout)
            
            # Apply initial theme
            self._apply_theme()
            
        except Exception as e:
            self.logger.error(f"Failed to setup UI: {e}")
    
    def _setup_themes(self):
        """Setup available themes - now dynamically loaded"""
        # Themes are now loaded in __init__ from src.ui.themes.py
        pass
    
    def _setup_animations(self):
        """Setup animations"""
        try:
            # Fade in animation
            self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
            self.fade_animation.setDuration(500)
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Start fade in
            self.fade_animation.start()
            
            # Setup emoji animation
            self._setup_emoji_animation()
            
        except Exception as e:
            self.logger.error(f"Failed to setup animations: {e}")
    
    def _setup_emoji_animation(self):
        """Setup the QPropertyAnimation for the floating emoji."""
        if not self.emoji_label: return

        self.emoji_animation = QPropertyAnimation(self.emoji_label, b"pos")
        self.emoji_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.emoji_animation.finished.connect(self._start_emoji_animation) # Chain animations

    def _start_emoji_animation(self):
        """Starts or restarts the emoji animation with random new target."""
        if not self.emoji_label or not self.config_manager.get('display.animated_emoji.enabled', False):
            self.emoji_label.hide()
            return
        
        # Ensure emoji is visible before animating
        self.emoji_label.show()

        # Get current position and window geometry
        current_pos = self.emoji_label.pos()
        window_rect = self.screen.geometry()
        emoji_size = self.config_manager.get('display.animated_emoji.size', 48)

        # Calculate bounds for random movement (consider emoji size)
        max_x = window_rect.width() - emoji_size
        max_y = window_rect.height() - emoji_size

        # Pick a random target position
        target_x = random.randint(0, max_x)
        target_y = random.randint(0, max_y)
        target_pos = QPoint(target_x, target_y)

        # Set animation start and end values
        self.emoji_animation.setStartValue(current_pos)
        self.emoji_animation.setEndValue(target_pos)

        # Set duration based on animation speed (1=fast, 20=slow)
        animation_speed_config = self.config_manager.get('display.animated_emoji.animation_speed', 5)
        # Map speed config (1-20) to duration (e.g., 2000ms to 10000ms)
        duration = 1000 + (animation_speed_config - 1) * (9000 / 19) 
        self.emoji_animation.setDuration(int(duration))

        # Start animation
        self.emoji_animation.start()

    def _stop_emoji_animation(self):
        """Stops the emoji animation and hides the emoji."""
        if self.emoji_animation and self.emoji_animation.state() == QPropertyAnimation.State.Running:
            self.emoji_animation.stop()
        if self.emoji_label: 
            self.emoji_label.hide()
    
    def _apply_theme(self):
        """Apply current theme"""
        try:
            theme_name = self.config_manager.get('display.theme', 'dark')
            theme = self.themes.get(theme_name, self.themes['dark'])
            
            # Set background
            self.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme['gradient_start'].name()},
                        stop:1 {theme['gradient_end'].name()});
                }}
            """)
            
            # Set font properties (make time font very large)
            font_size = self.config_manager.get('display.font_size', 120)
            font_family = self.config_manager.get('display.font_family', 'Segoe UI')
            time_font = QFont(font_family, font_size)
            self.time_label.setFont(time_font)
            date_font = QFont(font_family, max(24, font_size // 4))
            self.date_label.setFont(date_font)
            
            # Set window opacity
            self.setWindowOpacity(self.config_manager.get('display.opacity', 0.9))

            # Apply emoji styling and visibility
            emoji_enabled = self.config_manager.get('display.animated_emoji.enabled', False)
            if self.emoji_label:
                if emoji_enabled:
                    emoji_char = self.config_manager.get('display.animated_emoji.emoji', '✨')
                    emoji_size = self.config_manager.get('display.animated_emoji.size', 48)
                    self.emoji_label.setText(emoji_char)
                    self.emoji_label.setFont(QFont("Segoe UI Emoji", emoji_size))
                    self.emoji_label.setStyleSheet(f"color: {theme['accent'].name()};")
                    # Start animation if not already running
                    if self.emoji_animation and self.emoji_animation.state() != QPropertyAnimation.State.Running:
                        self._start_emoji_animation()
                else:
                    self._stop_emoji_animation()
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
    
    def _lazy_load_weather(self):
        if self._cached_config.get('display.show_weather', False) and self.weather_widget is None:
            try:
                self.weather_widget = WeatherWidget(self.config_manager)
                self.layout().addWidget(self.weather_widget)
            except Exception as e:
                self.logger.error(f"Failed to lazy load weather widget: {e}")
    
    def _update_display(self):
        """Update time and date display"""
        try:
            # Only update theme/weather if config has changed
            new_config = dict(self.config_manager.config) if hasattr(self.config_manager, 'config') else {}
            if new_config != self._cached_config:
                self._cached_config = new_config
                self._apply_theme()
            # Always update time and date
            now = datetime.now()
            time_format = self.config_manager.get('display.time_format', '24h')
            show_seconds = self.config_manager.get('display.show_seconds', True)
            if time_format == '12h':
                time_str = now.strftime('%I:%M')
                if show_seconds:
                    time_str += now.strftime(':%S')
                time_str += now.strftime(' %p')
            else:
                time_str = now.strftime('%H:%M')
                if show_seconds:
                    time_str += now.strftime(':%S')
            print(f"[DEBUG] Setting time_label: {time_str}")
            self.time_label.setText(time_str)
            # Date formatting
            date_format = self.config_manager.get('display.date_format', 'full')
            if date_format == 'full':
                date_str = now.strftime('%A, %B %d, %Y')
            elif date_format == 'short':
                date_str = now.strftime('%b %d, %Y')
            elif date_format == 'iso':
                date_str = now.strftime('%Y-%m-%d')
            else:
                date_str = now.strftime('%A, %B %d, %Y')
            print(f"[DEBUG] Setting date_label: {date_str}")
            self.date_label.setText(date_str)
            # Update To-Do Glass Card
            self._update_todo_card()
            # Weather display under time
            import requests
            show_weather = self.config_manager.get('display.show_weather', False)
            location = self.config_manager.get('weather.location', '')
            if show_weather and location:
                api_key = '8aa65584f01d432f9f5133344251906'
                url = 'http://api.weatherapi.com/v1/current.json'
                params = {'key': api_key, 'q': location, 'aqi': 'no'}
                resp = requests.get(url, params=params, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get('current', {})
                    cond = current.get('condition', {})
                    temp_c = current.get('temp_c')
                    text = cond.get('text', '')
                    # Emoji mapping
                    emoji = '❓'
                    desc = text.lower()
                    if 'sun' in desc or 'clear' in desc:
                        emoji = '☀️'
                    elif 'cloud' in desc:
                        emoji = '☁️'
                    elif 'rain' in desc or 'drizzle' in desc:
                        emoji = '🌧️'
                    elif 'snow' in desc:
                        emoji = '❄️'
                    elif 'storm' in desc or 'thunder' in desc:
                        emoji = '⛈️'
                    elif 'fog' in desc or 'mist' in desc:
                        emoji = '🌫️'
                    weather_str = f"{emoji} {temp_c}°C  {text}"
                    self.weather_label.setText(weather_str)
                    self.weather_label.show()
                else:
                    self.weather_label.setText("")
                    self.weather_label.hide()
            else:
                self.weather_label.setText("")
                self.weather_label.hide()
        except Exception as e:
            self.logger.error(f"Failed to update display: {e}")
    
    def _update_todo_card(self):
        # Remove old labels
        for label in getattr(self, 'todo_card_labels', []):
            self.todo_card_layout.removeWidget(label)
            label.deleteLater()
        self.todo_card_labels = []
        todos = self.config_manager.get('todo.items', [])
        show_todo = self.config_manager.get('display.show_todo', True)
        print(f"[DEBUG] To-Do items in config (screensaver): {todos}")
        if todos and show_todo:
            self.todo_card.show()
            for todo in todos:
                label = QLabel(f"\u2022 {todo}")
                label.setStyleSheet(
                    "color: #fff; font-size: 18px; font-family: 'Montserrat', 'Segoe UI', 'Arial', sans-serif; "
                    "font-weight: 600; letter-spacing: 1px; "
                    "text-shadow: 0 0 8px #00eaff, 0 0 2px #fff; background: transparent;"
                )
                label.setFont(QFont("Montserrat", 15, QFont.Weight.DemiBold))
                label.setWordWrap(True)
                label.setMinimumWidth(260)
                self.todo_card_layout.addWidget(label)
                self.todo_card_labels.append(label)
            # Dynamically set height based on number of items
            base_height = 60  # Title and padding
            item_height = 32  # Per item
            max_height = 320  # Max card height
            total_height = base_height + item_height * len(todos)
            if total_height > max_height:
                total_height = max_height
            self.todo_card.setFixedHeight(total_height)
            self.todo_card.setFixedWidth(400)
            self.todo_card_layout.setContentsMargins(28, 20, 28, 20)
            self.todo_card.adjustSize()
            x = self.width() - self.todo_card.width() - 30
            y = self.height() - self.todo_card.height() - 30
            if x < 0: x = 0
            if y < 0: y = 0
            self.todo_card.move(x, y)
            self.todo_card.raise_()
            print(f"[DEBUG] To-Do overlay shown at ({x}, {y}) with {len(todos)} items.")
        else:
            self.todo_card.hide()
            print("[DEBUG] To-Do overlay hidden.")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reposition the to-do card on resize
        if hasattr(self, 'todo_card') and self.todo_card.isVisible():
            self.todo_card.adjustSize()
            x = self.width() - self.todo_card.width() - 30
            y = self.height() - self.todo_card.height() - 30
            if x < 0: x = 0
            if y < 0: y = 0
            self.todo_card.move(x, y)
            self.todo_card.raise_()
    
    def update_config(self, config: Dict[str, Any]):
        """Update configuration"""
        try:
            # Reapply theme if needed
            self._apply_theme()
            
            # Update weather widget visibility
            show_weather = self.config_manager.get('display.show_weather', False)
            if show_weather and not self.weather_widget:
                self.weather_widget = WeatherWidget(self.config_manager)
                self.layout().addWidget(self.weather_widget)
            elif not show_weather and self.weather_widget:
                self.weather_widget.deleteLater()
                self.weather_widget = None
            
            # Update emoji animation state if enabled/disabled
            emoji_enabled = self.config_manager.get('display.animated_emoji.enabled', False)
            if emoji_enabled:
                if self.emoji_label and (not self.emoji_animation or self.emoji_animation.state() != QPropertyAnimation.State.Running):
                    self._start_emoji_animation()
                self._apply_theme() # Reapply theme to update emoji properties (char, size, color)
            else:
                self._stop_emoji_animation()
            
        except Exception as e:
            self.logger.error(f"Failed to update config: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        try:
            # Any key press closes the screensaver
            self.close()
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        try:
            # Any mouse click closes the screensaver
            self.close()
        except Exception as e:
            self.logger.error(f"Error handling mouse press: {e}")
    
    def closeEvent(self, event):
        """Handle close event"""
        try:
            # Stop update timer
            if self.update_timer:
                self.update_timer.stop()
            
            # Emit closed signal
            self.closed.emit()
            
            # Accept the close event
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error during close: {e}")
            event.accept()
    
    def _on_config_updated(self, config):
        print(f"[DEBUG] ScreensaverWindow received config_updated. To-Do: {self.config_manager.get('todo.items', [])}")
        self._update_display()
        self._update_todo_card() 