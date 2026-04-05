import sys
from loguru import logger
import os

def configure_logger(log_level: str = "INFO"):
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stderr, 
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    
    # File handler
    os.makedirs("reports/logs", exist_ok=True)
    logger.add(
        "reports/logs/execution_{time:YYYY_MM_DD}.log",
        level="DEBUG", # Always save DEBUG to file
        rotation="10 MB",
        retention="10 days"
    )
