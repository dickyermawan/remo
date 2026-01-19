# REMO - Logger Setup

import sys
from pathlib import Path
from loguru import logger

import config


def setup_logger():
    """Configure loguru logger for REMO."""
    
    # Create logs directory if not exists
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors (only if stdout is available)
    # Skip console logging when running with pythonw.exe (no console)
    if sys.stdout and hasattr(sys.stdout, 'write'):
        try:
            logger.add(
                sys.stdout,
                level=config.LOG_LEVEL,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
                       "<level>{message}</level>",
                colorize=True,
            )
        except Exception:
            # Silently fail if console not available (pythonw mode)
            pass
    
    # File handler with rotation (always enabled)
    logger.add(
        config.LOG_FILE,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info("Logger initialized")
    return logger


# Export configured logger
remo_logger = setup_logger()
