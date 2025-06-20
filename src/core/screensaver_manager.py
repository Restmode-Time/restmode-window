"""
Screensaver Manager
Handles inactivity detection, screensaver activation, and display management
"""

import logging
import time
import ctypes # For SendMessageW
from datetime import datetime, timedelta
from typing import Optional, List

from src.utils.qt_compat import QObject, QTimer, pyqtSignal, QThread, QApplication, QScreen

import psutil
import keyboard
import mouse
from pynput import mouse as pynput_mouse, keyboard as pynput_keyboard

from .config_manager import ConfigManager
from ..ui.screensaver_window import ScreensaverWindow

class InactivityMonitor(QThread):
    """Thread for monitoring user inactivity"""
    
    inactivity_detected = pyqtSignal()
    activity_detected = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.last_activity = time.time()
        self.check_interval = 1.0  # Check every second
        
        # Input listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
    def run(self):
        """Main monitoring loop"""
        self.running = True
        self.logger.info("Inactivity monitor started")
        
        # Start input listeners
        self._start_listeners()
        
        # Main monitoring loop
        while self.running:
            try:
                current_time = time.time()
                delay_minutes = self.config_manager.get('activation.delay_minutes', 5)
                delay_seconds = delay_minutes * 60
                
                # Check if user has been inactive for the specified time
                if current_time - self.last_activity >= delay_seconds:
                    # Inactivity detected, emit signal
                    self.inactivity_detected.emit()
                    
                # We still need to sleep to prevent busy-waiting
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in inactivity monitor: {e}")
                time.sleep(self.check_interval)
    
    def _start_listeners(self):
        """Start input listeners"""
        try:
            # Mouse listener
            self.mouse_listener = pynput_mouse.Listener(
                on_move=self._on_activity,
                on_click=self._on_activity,
                on_scroll=self._on_activity
            )
            self.mouse_listener.start()
            
            # Keyboard listener
            self.keyboard_listener = pynput_keyboard.Listener(
                on_press=self._on_activity,
                on_release=self._on_activity
            )
            self.keyboard_listener.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start input listeners: {e}")
    
    def _on_activity(self, *args):
        """Handle user activity"""
        self.last_activity = time.time()
        self.activity_detected.emit()
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        
        # Stop listeners
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            self.mouse_listener.join(1) # Wait for thread to finish
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            self.keyboard_listener.join(1) # Wait for thread to finish
        
        self.logger.info("Inactivity monitor stopped")

class ScreensaverManager(QObject):
    """Manages screensaver activation and display with optimized state logic"""
    
    # Signals
    screensaver_activated = pyqtSignal()
    screensaver_deactivated = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # State machine
        self.state = 'IDLE'  # Possible: IDLE, WAITING, ACTIVE
        self.is_active = False
        self.screensaver_windows: List[ScreensaverWindow] = []
        self.last_input_time = time.monotonic()
        self._last_polled_time = self.last_input_time
        self.last_media_check = 0
        self.media_active = False
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_inactivity)
        self.screensaver_off_timer = QTimer()
        self.screensaver_off_timer.setSingleShot(True)
        self.screensaver_off_timer.timeout.connect(self._turn_off_screen)
        self._setup_global_hotkeys()
        self.config_manager.config_updated.connect(self._on_config_updated)
        # Setup input listeners
        self._setup_input_listeners()
        if self.config_manager.get('activation.enable_auto_activation', True):
            self.start_monitoring()
    
    def _setup_global_hotkeys(self):
        """Setup global keyboard shortcuts"""
        try:
            # Manual activation/deactivation
            keyboard.add_hotkey('ctrl+alt+s', self.toggle_screensaver)
            
            # Emergency exit
            keyboard.add_hotkey('ctrl+alt+q', self.deactivate_screensaver)
            
        except Exception as e:
            self.logger.error(f"Failed to setup global hotkeys: {e}")
    
    def start_monitoring(self):
        """Start inactivity polling"""
        interval = self.config_manager.get('activation.check_interval_seconds', 30)
        self.poll_timer.start(interval * 1000)
        self.logger.info("Inactivity polling started")
    
    def stop_monitoring(self):
        self.poll_timer.stop()
        self.logger.info("Inactivity polling stopped")
    
    def _poll_inactivity(self):
        now = time.monotonic()
        delay_minutes = self.config_manager.get('activation.delay_minutes', 5)
        delay_seconds = delay_minutes * 60
        if self._user_is_active():
            self.last_input_time = now
            if self.state != 'IDLE':
                self._set_state('IDLE')
            return
        # Video detection: skip activation if video is playing
        if self._is_video_playing():
            self._set_state('WAITING')
            return
        if now - self.last_input_time >= delay_seconds:
            if self.state != 'ACTIVE':
                self._activate_screensaver()
                self._set_state('ACTIVE')
        else:
            self._set_state('WAITING')
    
    def _set_state(self, new_state):
        if self.state != new_state:
            self.logger.info(f"State changed: {self.state} -> {new_state}")
            self.state = new_state
    
    def _user_is_active(self):
        # Return True if there was input since the last poll
        if getattr(self, '_input_activity', False):
            self._input_activity = False
            return True
        return False
    
    def _is_system_active(self) -> bool:
        try:
            import win32gui
            import win32con
            import win32process
            import os

            current_pid = os.getpid()

            def is_blocking_window(hwnd):
                # Only consider windows not belonging to this process
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == current_pid:
                        return False
                except Exception:
                    pass
                # Only block if visible and not minimized
                if not win32gui.IsWindowVisible(hwnd):
                    return False
                if win32gui.IsIconic(hwnd):  # Minimized
                    return False
                exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if exstyle & win32con.WS_EX_TOOLWINDOW:
                    return False
                title = win32gui.GetWindowText(hwnd)
                if not title.strip():
                    return False
                return True

            blocking_windows = []
            def enum_handler(hwnd, ctx):
                if is_blocking_window(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    blocking_windows.append(title)

            win32gui.EnumWindows(enum_handler, None)

            if blocking_windows:
                for title in blocking_windows:
                    self.logger.info(f"Blocking window '{title}' is open, visible, and not minimized. System is active.")
                return True
            else:
                self.logger.info("No blocking windows found (all are minimized or invisible). System is inactive. Screensaver can activate.")
                return False
        except Exception as e:
            self.logger.error(f"Error checking system-wide window state: {e}")
            return False
    
    def _activate_screensaver(self):
        try:
            if self.is_active:
                return
            self.logger.info("Activating screensaver...")
            app = QApplication.instance()
            screens = app.screens()
            for screen in screens:
                window = ScreensaverWindow(screen, self.config_manager)
                window.closed.connect(self.deactivate_screensaver)
                self.screensaver_windows.append(window)
                window.showFullScreen()
            self.is_active = True
            self.screensaver_activated.emit()
            self.stop_monitoring()
            turn_off_delay = self.config_manager.get('system.turn_off_screen_delay_minutes', 0)
            if turn_off_delay > 0:
                self.screensaver_off_timer.start(turn_off_delay * 60 * 1000)
                self.logger.info(f"Screen off timer started for {turn_off_delay} minutes")
        except Exception as e:
            self.logger.error(f"Failed to activate screensaver: {e}")
            self.error_occurred.emit(f"Screensaver activation error: {e}")
    
    def deactivate_screensaver(self):
        try:
            if not self.is_active:
                return
            self.logger.info("Deactivating screensaver...")
            if self.screensaver_off_timer.isActive():
                self.screensaver_off_timer.stop()
                self.logger.info("Screen off timer stopped")
            for window in self.screensaver_windows:
                window.close()
            self.screensaver_windows.clear()
            self.is_active = False
            self.screensaver_deactivated.emit()
            if self.config_manager.get('activation.enable_auto_activation', True):
                self.start_monitoring()
        except Exception as e:
            self.logger.error(f"Failed to deactivate screensaver: {e}")
            self.error_occurred.emit(f"Screensaver deactivation error: {e}")
    
    def _turn_off_screen(self):
        self.logger.info("Attempting to turn off screen...")
        try:
            HWND_BROADCAST = 0xFFFF
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            MONITOR_OFF = 2
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF)
            self.logger.info("Screen turn off signal sent.")
        except Exception as e:
            self.logger.error(f"Failed to turn off screen: {e}")
            self.error_occurred.emit(f"Screen turn off error: {e}")
    
    def toggle_screensaver(self):
        if self.is_active:
            self.deactivate_screensaver()
        else:
            self._activate_screensaver()
    
    def _on_config_updated(self, config: dict):
        self.logger.info("Configuration updated. Applying changes...")
        interval = self.config_manager.get('activation.check_interval_seconds', 30)
        self.poll_timer.setInterval(interval * 1000)
        if self.config_manager.get('activation.enable_auto_activation', True):
            if not self.poll_timer.isActive():
                self.start_monitoring()
        else:
            if self.poll_timer.isActive():
                self.stop_monitoring()
        if self.screensaver_off_timer.isActive():
            turn_off_delay = self.config_manager.get('system.turn_off_screen_delay_minutes', 0)
            if turn_off_delay > 0:
                self.screensaver_off_timer.start(turn_off_delay * 60 * 1000)
            else:
                self.screensaver_off_timer.stop()
    
    def cleanup(self):
        self.logger.info("Performing ScreensaverManager cleanup...")
        self.stop_monitoring()
        self.deactivate_screensaver()
        try:
            self.config_manager.config_updated.disconnect(self._on_config_updated)
            self.screensaver_off_timer.timeout.disconnect(self._turn_off_screen)
        except TypeError:
            pass
        self.logger.info("ScreensaverManager cleanup complete.")

    def _setup_input_listeners(self):
        self._input_activity = False
        def on_mouse(*args):
            self._input_activity = True
        def on_keyboard(*args):
            self._input_activity = True
        self._mouse_listener = pynput_mouse.Listener(
            on_move=on_mouse,
            on_click=on_mouse,
            on_scroll=on_mouse
        )
        self._keyboard_listener = pynput_keyboard.Listener(
            on_press=on_keyboard,
            on_release=on_keyboard
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def _is_video_playing(self) -> bool:
        """Detect if a fullscreen video is likely playing (browser or video player)."""
        try:
            import win32gui
            import win32process
            import win32con
            import os

            # List of known video player and browser process names
            video_apps = [
                'vlc.exe', 'potplayer.exe', 'mpc-hc.exe', 'mpc-be.exe', 'wmplayer.exe',
                'chrome.exe', 'msedge.exe', 'firefox.exe', 'opera.exe', 'brave.exe',
                'iexplore.exe', 'moviesandtv.exe', 'netflix.exe', 'disneyplus.exe'
            ]
            def is_fullscreen(hwnd):
                if not win32gui.IsWindowVisible(hwnd):
                    return False
                rect = win32gui.GetWindowRect(hwnd)
                from win32api import GetSystemMetrics
                sw = GetSystemMetrics(0)
                sh = GetSystemMetrics(1)
                # Allow for taskbar, so check if window covers most of the screen
                return (rect[2] - rect[0] >= sw - 10) and (rect[3] - rect[1] >= sh - 40)
            def is_video_window(hwnd):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    import psutil
                    proc = psutil.Process(pid)
                    exe = proc.name().lower()
                    if exe in video_apps and is_fullscreen(hwnd):
                        return True
                except Exception:
                    pass
                return False
            found = False
            def enum_handler(hwnd, ctx):
                nonlocal found
                if is_video_window(hwnd):
                    found = True
            win32gui.EnumWindows(enum_handler, None)
            return found
        except Exception as e:
            self.logger.error(f"Error in video detection: {e}")
            return False 