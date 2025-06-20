"""
Worker Thread Utility
Provides a generic QThread for running tasks in the background to prevent UI freezes.
"""

import traceback
import sys
import logging
from typing import Callable, Any
from src.utils.qt_compat import QThread, pyqtSignal, QObject

class Worker(QObject):
    """Worker object that executes a function in a separate thread.
    
    Signals:
        finished: Emitted when the worker's task has completed (successfully or with error).
        error: Emitted when an exception occurs during the task execution.
        result: Emitted with the result of the task if successful.
    """
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    result = pyqtSignal(object)

    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Executes the stored function and emits signals based on success or failure."""
        try:
            res = self._func(*self._args, **self._kwargs)
            self.result.emit(res)
        except Exception:
            traceback_str = traceback.format_exc()
            error_message = f"Error in worker thread: {sys.exc_info()[1]}"
            self.logger.error(f"{error_message}\n{traceback_str}")
            self.error.emit(error_message, traceback_str)
        finally:
            self.finished.emit()

class WorkerThread(QThread):
    """Manages a Worker object to run a function in a separate thread.
    
    Usage:
        def my_long_running_function(data):
            # ... perform long task ...
            return result
            
        thread = WorkerThread(my_long_running_function, my_data)
        thread.signals.result.connect(on_result)
        thread.signals.error.connect(on_error)
        thread.signals.finished.connect(on_finished)
        thread.start()
    """
    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        super().__init__()
        self._worker = Worker(func, *args, **kwargs)
        self._worker.moveToThread(self)
        self.started.connect(self._worker.run)
        self._worker.finished.connect(self.quit) # Quit the thread when worker finishes
        self._worker.finished.connect(self.deleteLater) # Clean up the worker object
        self.finished.connect(self._worker.deleteLater) # Clean up the worker thread itself
        
        self.signals = self._worker # Expose worker signals directly

    def start(self, priority: QThread.Priority = QThread.Priority.NormalPriority) -> None:
        super().start(priority) 