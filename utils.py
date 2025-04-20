import logging
import os
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Create formatter and add to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def timestamp():
    """Return current timestamp as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_activity(logger, activity_type, details):
    """Log an activity with standardized format."""
    logger.info(f"ACTIVITY: {activity_type} - {details}")

def log_alert(logger, alert_level, message):
    """Log an alert with appropriate level."""
    if alert_level.lower() == "low":
        logger.warning(f"ALERT (LOW): {message}")
    elif alert_level.lower() == "medium":
        logger.warning(f"ALERT (MEDIUM): {message}")
    elif alert_level.lower() == "high":
        logger.error(f"ALERT (HIGH): {message}")
    else:
        logger.warning(f"ALERT: {message}") 