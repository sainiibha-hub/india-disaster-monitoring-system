"""
logger_config.py
Centralized logging setup. Every module calls get_logger(__name__) to get a
logger that writes to both the console and a rotating log file under logs/.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config import LOG_DIR

LOG_FILE = os.path.join(LOG_DIR, "disaster_monitoring.log")

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Safe to call repeatedly (handlers are
    only attached once per logger name)."""
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured (avoids duplicate log lines on repeated imports)
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
