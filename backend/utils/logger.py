"""
Utils Logger.

Provides a pre-configured logger for utility modules.
Thin wrapper around core.logger to avoid circular imports
when utils modules need logging.
"""

import logging
import sys
from pathlib import Path


def get_util_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Create a utility-level logger.

    Args:
        name: Logger name (use __name__ in your module).
        log_file: Optional path for a log file.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Optional file handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


# Pre-configured util logger
util_logger = get_util_logger("career_coach.utils")
