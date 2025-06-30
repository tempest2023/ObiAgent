"""
Logging configuration for the PocketFlow General Agent System

This module provides logging configuration for different environments:
- DEBUG: Detailed logging for development
- INFO: Standard logging for production
- QUIET: Minimal logging for performance
"""

import logging
import os
import sys
from typing import Optional

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'QUIET')
        log_file: Optional file path to write logs to
    """
    
    # Convert level to logging constant
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'QUIET': logging.ERROR  # Only errors in quiet mode
    }
    
    log_level = level_map.get(level.upper(), logging.INFO)
    
    # Create formatter
    if level.upper() == 'DEBUG':
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    loggers_to_configure = [
        'agent.nodes',
        'agent.flow',
        'agent.utils',
        'server',
        'pocketflow'
    ]
    
    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = True
    
    # Log the configuration
    if level.upper() != 'QUIET':
        logging.info(f"🔧 Logging configured - Level: {level}, File: {log_file or 'console only'}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

# Environment-based configuration
def setup_environment_logging():
    """Setup logging based on environment variables"""
    level = os.environ.get('LOG_LEVEL', 'INFO')
    log_file = os.environ.get('LOG_FILE')
    
    setup_logging(level, log_file)

# Convenience functions for different logging modes
def setup_debug_logging(log_file: Optional[str] = None):
    """Setup debug logging for development"""
    setup_logging('DEBUG', log_file)

def setup_info_logging(log_file: Optional[str] = None):
    """Setup info logging for production"""
    setup_logging('INFO', log_file)

def setup_quiet_logging(log_file: Optional[str] = None):
    """Setup quiet logging for performance"""
    setup_logging('QUIET', log_file)

# Auto-setup if this module is imported
if __name__ != "__main__":
    setup_environment_logging() 