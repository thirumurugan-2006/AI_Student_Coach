import logging
import sys
from pathlib import Path
from config.settings import get_settings

settings = get_settings()

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Configures and returns a logger instance.
    Ensures a consistent logging format across the application.
    
    Args:
        name: Logger name.
        log_file: Optional log file path for file logging.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger

# Create default loggers for different components
api_logger = setup_logger("career_coach.api")
database_logger = setup_logger("career_coach.database")
auth_logger = setup_logger("career_coach.auth")
error_logger = setup_logger("career_coach.error")

# Default logger for backward compatibility
logger = setup_logger("career_coach")
