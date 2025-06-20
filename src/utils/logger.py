"""
Logging Utility
Provides comprehensive logging functionality for the application
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Setup comprehensive logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    try:
        # Create logs directory
        logs_dir = Path.home() / ".screensaver" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Default log file if not specified
        if not log_file:
            log_file = logs_dir / f"screensaver_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = logs_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=2*1024*1024,  # 2MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized")
        logger.info(f"Log level: {log_level}")
        logger.info(f"Log file: {log_file}")
        
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.error(f"Failed to setup logging: {e}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_function_call(func):
    """
    Decorator to log function calls
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised exception: {e}")
            raise
    return wrapper

def log_performance(func):
    """
    Decorator to log function performance
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.debug(f"{func.__name__} took {duration:.4f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"{func.__name__} failed after {duration:.4f} seconds: {e}")
            raise
    return wrapper

class LogContext:
    """Context manager for logging operations"""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation} in {duration:.4f} seconds")
        else:
            self.logger.error(f"Failed {self.operation} after {duration:.4f} seconds: {exc_val}")

def cleanup_old_logs(days_to_keep: int = 30):
    """
    Clean up old log files
    
    Args:
        days_to_keep: Number of days to keep log files
    """
    try:
        from datetime import timedelta
        
        logs_dir = Path.home() / ".screensaver" / "logs"
        if not logs_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for log_file in logs_dir.glob("*.log"):
            try:
                # Try to get file modification time
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                logging.warning(f"Failed to process log file {log_file}: {e}")
        
        if deleted_count > 0:
            logging.info(f"Cleaned up {deleted_count} old log files")
            
    except Exception as e:
        logging.error(f"Failed to cleanup old logs: {e}") 