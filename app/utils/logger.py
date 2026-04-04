import logging
import logging.handlers
import os
import sys
from queue import Queue
from app.utils.context import get_request_id

# Configuration
LOG_DIR = "logs"
APP_LOG = os.path.join(LOG_DIR, "app.log")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")

# Professional format: Time,ms - PID [Thread] LEVEL Logger - RequestID - Message
LOG_FORMAT = "%(asctime)s,%(msecs)03d - %(process)d [%(threadName)s] %(levelname)-5s %(name)s - %(request_id)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

# Global queue for non-blocking logging
log_queue = Queue(-1)

class LogCorrelationFilter(logging.Filter):
    """
    Injects the request_id from the current context into every log record.
    """
    def filter(self, record):
        record.request_id = get_request_id()
        return True

def setup_logging():
    """
    Sets up a production-grade, non-blocking logging system.
    Includes automatic request ID tracking and thread/process identification.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Correlation filter must be added to all handlers
    correlation_filter = LogCorrelationFilter()

    # Correlation filter must be added to the root logger to capture context 
    # BEFORE the record is sent to the background queue.
    correlation_filter = LogCorrelationFilter()
    root_logger.addFilter(correlation_filter)

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    console_handler.setLevel(logging.INFO)

    # 2. App Log Handler
    app_handler = logging.handlers.RotatingFileHandler(
        APP_LOG, maxBytes=20*1024*1024, backupCount=10, encoding="utf-8"
    )
    app_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    app_handler.setLevel(logging.INFO)

    # 3. Error Log Handler
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG, maxBytes=20*1024*1024, backupCount=10, encoding="utf-8"
    )
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    error_handler.setLevel(logging.ERROR)

    # Queue Listener to handle file I/O in a separate thread
    listener = logging.handlers.QueueListener(
        log_queue, console_handler, app_handler, error_handler, respect_handler_level=True
    )
    listener.start()

    # Queue Handler to redirect all logs to the queue
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.addFilter(correlation_filter)  # <--- Essential for all loggers
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(queue_handler)

    # Essential: Ensure Uvicorn logs also use our high-fidelity format
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = [queue_handler]
        logger.propagate = False  # Prevent double logging
    
    logging.info("Logging system upgraded to Production Grade (Auto Correlation Active)")
    
    return listener

def get_logger(name: str):
    return logging.getLogger(name)
