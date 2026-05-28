import logging
import logging.handlers
from typing import Optional
from config.settings import Settings

def setup_logger(name: str = "optilogix") -> logging.Logger:
    """
    Initializes a highly descriptive, multi-handler logger.
    Logs to console and dynamically rolls files based on size limits.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
        
    logger.setLevel(Settings.LOG_LEVEL)
    
    # Define standard format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s"
    )
    
    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(Settings.LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. Rotating File Handler
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            str(Settings.LOG_FILE_PATH),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(Settings.LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Failed to initialize rotating file log handler: {e}")
        
    logger.info("OptiLogix Logging Subsystem initialized successfully.")
    return logger
