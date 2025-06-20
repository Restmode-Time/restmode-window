"""
Configuration Manager
Handles application settings, dashboard integration, and remote configuration
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from src.utils.qt_compat import QObject, pyqtSignal, QTimer
from src.utils.worker_thread import WorkerThread

class ConfigManager(QObject):
    """Manages application configuration and dashboard integration"""
    
    # Signals
    config_updated = pyqtSignal(dict)
    dashboard_sync_completed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    dashboard_sync_status = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.dashboard_sync_thread = None
        
        # Configuration file path
        self.config_dir = Path.home() / ".screensaver"
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.default_config = {
            "activation": {
                "delay_minutes": 5,
                "check_interval_seconds": 30,
                "enable_auto_activation": True
            },
            "display": {
                "theme": "dark",
                "time_format": "24h",
                "date_format": "full",
                "font_size": 72,
                "font_family": "Segoe UI",
                "font_style": "normal",
                "opacity": 0.9,
                "show_seconds": True,
                "show_date": True,
                "show_weather": False,
                "animated_emoji": {
                    "enabled": False,
                    "emoji": "✨",
                    "size": 48,
                    "animation_speed": 5
                },
                "show_todo": True
            },
            "system": {
                "startup_enabled": False,
                "system_tray_enabled": True,
                "multi_monitor": True,
                "low_power_mode": True
            },
            "weather": {
                "api_key": "",
                "location": "",
                "units": "metric"
            }
        }
        
        # Current configuration
        self.config = self.default_config.copy()
        
        # Initialize
        self._ensure_config_dir()
        self.load_config()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
                    self.logger.info("Configuration loaded successfully")
            else:
                self.save_config()
                self.logger.info("Default configuration created")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.error_occurred.emit(f"Configuration load error: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            self.error_occurred.emit(f"Configuration save error: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing config"""
        def merge_dicts(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(self.config, new_config)
    
    def get(self, key_path: str, default=None):
        """Get configuration value by dot-separated path"""
        try:
            keys = key_path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value by dot-separated path"""
        try:
            keys = key_path.split('.')
            config = self.config
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            config[keys[-1]] = value
            self.save_config()
            self.config_updated.emit(self.config)
        except Exception as e:
            self.logger.error(f"Failed to set configuration {key_path}: {e}")
            self.error_occurred.emit(f"Configuration set error: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        try:
            self.config = self.default_config.copy()
            self.save_config()
            self.config_updated.emit(self.config)
            self.logger.info("Configuration reset to defaults")
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            self.error_occurred.emit(f"Configuration reset error: {e}")
    
    def export_config(self, file_path: Path):
        """Export configuration to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            self.error_occurred.emit(f"Configuration export error: {e}")
    
    def import_config(self, file_path: Path):
        """Import configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            self._merge_config(imported_config)
            self.save_config()
            self.config_updated.emit(self.config)
            self.logger.info(f"Configuration imported from {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            self.error_occurred.emit(f"Configuration import error: {e}") 