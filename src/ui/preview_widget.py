"""
Preview Widget
Live preview of screensaver settings
"""

import logging
from datetime import datetime
from src.utils.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTimer, Qt, QFont, QSizePolicy, QPalette, QGraphicsOpacityEffect, QFrame, QListWidget, QListWidgetItem
)
from ..core.config_manager import ConfigManager
from .themes import get_themes

class PreviewWidget(QWidget):
    """Widget for previewing screensaver settings"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._last_settings = None  # Store last settings for clock updates
    
    def _setup_ui(self):
        """Setup the preview UI"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Time label
            self.time_label = QLabel()
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.time_label)
            
            # Date label
            self.date_label = QLabel()
            self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.date_label)
            
            # Weather label (placeholder)
            self.weather_label = QLabel()
            self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.weather_label)
            
            # To-Do Card Overlay
            self.todo_card = QFrame(self)
            self.todo_card.setObjectName("TodoCard")
            self.todo_card.setStyleSheet("""
                QFrame#TodoCard {
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(30,30,40,0.85),
                        stop:1 rgba(30,30,40,0.65)
                    );
                    border-radius: 28px;
                }
            """)
            self.todo_card.setFixedWidth(220)
            self.todo_card_layout = QVBoxLayout(self.todo_card)
            self.todo_card_layout.setContentsMargins(12, 8, 12, 8)
            self.todo_card_title = QLabel("To-Do Reminder")
            self.todo_card_title.setStyleSheet("font-weight: bold; color: #fff; font-size: 13px;")
            self.todo_card_layout.addWidget(self.todo_card_title)
            # Use QListWidget for scrollable to-do items
            self.todo_list_widget = QListWidget(self.todo_card)
            self.todo_list_widget.setStyleSheet("color: #fff; font-size: 13px; font-family: 'Segoe UI', 'Arial', sans-serif; background: transparent; border: none;")
            self.todo_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.todo_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.todo_list_widget.setFixedHeight(80)
            self.todo_card_layout.addWidget(self.todo_list_widget)
            self.todo_card_labels = []
            self.todo_card.hide()
            
            layout.addStretch()
            self.setLayout(layout)
            
        except Exception as e:
            self.logger.error(f"Failed to setup preview UI: {e}")
    
    def update_from_settings(self, settings):
        """Update the preview using a settings dictionary (for live preview)"""
        self._last_settings = settings.copy()
        self._update_preview(settings)
        self._update_todo_card(settings)

    def _update_preview(self, settings=None):
        """Update the preview display using the latest settings (or config if none)"""
        try:
            if settings is None:
                settings = self._last_settings or {
                    'theme': 'dark',
                    'time_format': '24h',
                    'show_seconds': True,
                    'font_size': 72,
                    'font_family': 'Segoe UI',
                    'font_style': 'normal',
                    'opacity': 0.9,
                    'show_date': True,
                    'date_format': 'full',
                }
            theme = settings.get('theme', 'dark')
            time_format = settings.get('time_format', '24h')
            show_seconds = settings.get('show_seconds', True)
            font_size = settings.get('font_size', 72)
            font_family = settings.get('font_family', 'Segoe UI')
            font_style = settings.get('font_style', 'normal')
            opacity = settings.get('opacity', 0.9)
            show_date = settings.get('show_date', True)
            date_format = settings.get('date_format', 'full')

            themes = get_themes()
            theme_colors = themes.get(theme, themes['dark'])
            bg_color = theme_colors['background']
            text_color = theme_colors['text']

            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, bg_color)
            palette.setColor(QPalette.ColorRole.WindowText, text_color)
            self.setPalette(palette)
            self.setAutoFillBackground(True)

            # Apply opacity effect
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(opacity)
            self.setGraphicsEffect(effect)

            from datetime import datetime
            now = datetime.now()
            if time_format == '12h':
                time_str = now.strftime('%I:%M')
                if show_seconds:
                    time_str += now.strftime(':%S')
                time_str += now.strftime(' %p')
            else:
                time_str = now.strftime('%H:%M')
                if show_seconds:
                    time_str += now.strftime(':%S')

            # Date formatting
            if show_date:
                if date_format == 'full':
                    date_str = now.strftime('%A, %B %d, %Y')
                elif date_format == 'short':
                    date_str = now.strftime('%b %d, %Y')
                elif date_format == 'iso':
                    date_str = now.strftime('%Y-%m-%d')
                else:
                    date_str = now.strftime('%A, %B %d, %Y')
                self.date_label.setText(date_str)
                self.date_label.show()
            else:
                self.date_label.hide()

            # Set fonts
            time_font = QFont(font_family, font_size // 2)
            if font_style == 'italic':
                time_font.setItalic(True)
            date_font = QFont(font_family, font_size // 4)
            if font_style == 'italic':
                date_font.setItalic(True)
            self.time_label.setFont(time_font)
            self.date_label.setFont(date_font)
            self.weather_label.setFont(date_font)

            self.time_label.setText(time_str)

            # Weather display
            try:
                from PySide6.QtWidgets import QLabel
                import requests
                location = self.config_manager.get('weather.location', '')
                show_weather = self.config_manager.get('display.show_weather', False)
                if show_weather and location:
                    api_key = '8aa65584f01d432f9f5133344251906'
                    url = 'http://api.weatherapi.com/v1/current.json'
                    params = {'key': api_key, 'q': location, 'aqi': 'no'}
                    try:
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
                    except Exception:
                        self.weather_label.setText("")
                        self.weather_label.hide()
                else:
                    self.weather_label.setText("")
                    self.weather_label.hide()
            except Exception:
                self.weather_label.setText("")
                self.weather_label.hide()
        except Exception as e:
            self.logger.error(f"Failed to update preview from settings: {e}")

    def _update_todo_card(self, settings=None):
        # Remove old labels
        for label in getattr(self, 'todo_card_labels', []):
            self.todo_card_layout.removeWidget(label)
            label.deleteLater()
        self.todo_card_labels = []
        # Use todo_items from settings if provided, else from config
        todos = []
        if settings and 'todo_items' in settings:
            todos = settings['todo_items']
        elif hasattr(self, 'config_manager'):
            todos = self.config_manager.get('todo.items', [])
        show_todo = self.config_manager.get('display.show_todo', True)
        print(f"[DEBUG] PreviewWidget received todos: {todos}")
        if todos and show_todo:
            self.todo_card.show()
            self.todo_list_widget.clear()
            for todo in todos:
                item = QListWidgetItem(f"\u2022 {todo}")
                item.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
                self.todo_list_widget.addItem(item)
            # Adjust card height
            base_height = 32  # Title and padding
            max_height = 110  # Max card height
            self.todo_card.setFixedHeight(base_height + self.todo_list_widget.height())
            self.todo_card.adjustSize()
            x = self.width() - self.todo_card.width() - 12
            y = self.height() - self.todo_card.height() - 12
            if x < 0: x = 0
            if y < 0: y = 0
            self.todo_card.move(x, y)
            self.todo_card.raise_()
        else:
            self.todo_card.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reposition the to-do card on resize
        if self.todo_card.isVisible():
            self.todo_card.adjustSize()
            x = self.width() - self.todo_card.width() - 12
            y = self.height() - self.todo_card.height() - 12
            if x < 0: x = 0
            if y < 0: y = 0
            self.todo_card.move(x, y)
            self.todo_card.raise_()

    def cleanup(self):
        """Cleanup resources"""
        pass 