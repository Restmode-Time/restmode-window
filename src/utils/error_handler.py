"""
Error Handler
Provides graceful error handling and user notification
"""

import logging
import traceback
import sys
from typing import Optional, Callable
from src.utils.qt_compat import QMessageBox, QApplication, QObject, pyqtSignal

class ErrorHandler(QObject):
    """Centralized error handling for the application"""
    
    # Signals
    error_occurred = pyqtSignal(str)
    critical_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.error_callbacks = []
        self.critical_error_callbacks = []
        
    def handle_error(self, error: str, show_dialog: bool = True, critical: bool = False):
        """
        Handle an error with logging and optional user notification
        
        Args:
            error: Error message
            show_dialog: Whether to show error dialog to user
            critical: Whether this is a critical error
        """
        try:
            # Log the error
            if critical:
                self.logger.critical(error)
                self.critical_error.emit(error)
            else:
                self.logger.error(error)
                self.error_occurred.emit(error)
            
            # Show dialog if requested
            if show_dialog:
                self._show_error_dialog(error, critical)
            
            # Call registered callbacks
            callbacks = self.critical_error_callbacks if critical else self.error_callbacks
            for callback in callbacks:
                try:
                    callback(error)
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
                    
        except Exception as e:
            # Fallback error handling
            print(f"Error in error handler: {e}")
            print(f"Original error: {error}")
    
    def handle_exception(self, exc_type, exc_value, exc_traceback, show_dialog: bool = True):
        """
        Handle an exception with full traceback
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
            show_dialog: Whether to show error dialog to user
        """
        try:
            # Format the exception
            error_msg = f"Exception: {exc_type.__name__}: {exc_value}"
            traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            
            # Log the full traceback
            self.logger.error(f"{error_msg}\n{traceback_str}")
            
            # Show user-friendly error
            if show_dialog:
                self._show_error_dialog(error_msg, critical=False)
                
        except Exception as e:
            print(f"Error handling exception: {e}")
    
    def _show_error_dialog(self, error: str, critical: bool = False):
        """Show error dialog to user"""
        try:
            # Check if QApplication exists
            app = QApplication.instance()
            if not app:
                return
            
            # Create dialog
            if critical:
                icon = QMessageBox.Icon.Critical
                title = "Critical Error"
            else:
                icon = QMessageBox.Icon.Warning
                title = "Error"
            
            msg_box = QMessageBox()
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText("An error occurred in the Desktop Screensaver application.")
            msg_box.setInformativeText(error)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            # Show dialog
            msg_box.exec()
            
        except Exception as e:
            # Fallback to console output
            print(f"Failed to show error dialog: {e}")
            print(f"Error: {error}")
    
    def register_error_callback(self, callback: Callable[[str], None]):
        """Register a callback for error events"""
        self.error_callbacks.append(callback)
    
    def register_critical_error_callback(self, callback: Callable[[str], None]):
        """Register a callback for critical error events"""
        self.critical_error_callbacks.append(callback)
    
    def setup_global_exception_handler(self):
        """Setup global exception handler"""
        try:
            sys.excepthook = self._global_exception_handler
            self.logger.info("Global exception handler installed")
        except Exception as e:
            self.logger.error(f"Failed to setup global exception handler: {e}")
    
    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler for unhandled exceptions"""
        try:
            # Don't handle KeyboardInterrupt
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Handle the exception
            self.handle_exception(exc_type, exc_value, exc_traceback, show_dialog=True)
            
        except Exception as e:
            # Fallback to default handler
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, error_handler: ErrorHandler, operation: str, show_dialog: bool = True):
        self.error_handler = error_handler
        self.operation = operation
        self.show_dialog = show_dialog
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_msg = f"Error in {self.operation}: {exc_val}"
            self.error_handler.handle_error(error_msg, self.show_dialog)
            return True  # Suppress the exception
        return False

def safe_execute(func: Callable, error_handler: ErrorHandler, operation: str = None, *args, **kwargs):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        error_handler: Error handler instance
        operation: Description of the operation
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        op_name = operation or func.__name__
        error_msg = f"Error in {op_name}: {e}"
        error_handler.handle_error(error_msg)
        return None

def retry_on_error(func: Callable, max_retries: int = 3, delay: float = 1.0, error_handler: ErrorHandler = None):
    """
    Decorator to retry function on error
    
    Args:
        func: Function to decorate
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        error_handler: Error handler instance
        
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    if error_handler:
                        error_handler.handle_error(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}",
                            show_dialog=False
                        )
                    time.sleep(delay)
                else:
                    if error_handler:
                        error_handler.handle_error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
                    raise last_exception
        
        raise last_exception
    
    return wrapper 