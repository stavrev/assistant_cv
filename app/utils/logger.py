"""
Logger module for the CV Assistant application.

This module provides a consistent logging interface for the entire application,
including console output and rotatable log files.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict


# Cache for loggers to avoid creating multiple handlers for the same logger
_logger_cache: Dict[str, logging.Logger] = {}

# Log directory
LOG_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / 'logs'

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# Log levels for different outputs
CONSOLE_LEVEL = logging.WARNING  # Only warnings and errors for console
FILE_LEVEL = logging.DEBUG      # Very verbose for log files

# Log format for different outputs
CONSOLE_FORMAT = '%(message)s'  # Simplified format without timestamp for console
FILE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Detailed format for log files

# Date format
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Maximum log file size (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024

# Number of backup files to keep
BACKUP_COUNT = 5


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with both console and file handlers.
    All logs are unified in a single run.log file.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, return it
    if logger.handlers:
        return logger
    
    # Set the logger level to the minimum of the two handlers
    logger.setLevel(min(CONSOLE_LEVEL, FILE_LEVEL))
    
    # We don't want to add a console handler here
    # Console output will be handled directly via print statements in the code
    # This ensures the log file has all the detailed information while console remains clean
    
    # Create file handler with rotation - unified log file
    log_file = LOG_DIR / "run.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(FILE_LEVEL)
    file_formatter = logging.Formatter(FILE_FORMAT, DATE_FORMAT)
    # Add formatter to file handler
    file_handler.setFormatter(file_formatter)
    
    # Add file handler to logger
    logger.addHandler(file_handler)
    
    # Cache the logger
    _logger_cache[name] = logger
    
    return logger


def get_pipeline_logger(pipeline_name: str) -> logging.Logger:
    """
    Get a logger specifically for a pipeline.
    
    Args:
        pipeline_name: Name of the pipeline (cv, letter, adopt)
        
    Returns:
        Configured logger instance for the pipeline
    """
    return get_logger(f'app.pipelines.{pipeline_name}')
