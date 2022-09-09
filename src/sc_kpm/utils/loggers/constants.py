import logging
from dataclasses import dataclass

CONSOLE_HANDLER = "console_handler"
TO_FILE_HANDLER = "to_file_handler"
LOGGER = "logger"


@dataclass(frozen=True)
class Level:
    INFO: str = "info"
    WARNING: str = "warning"
    DEBUG: str = "debug"
    ERROR: str = "error"
    CRITICAL: str = "critical"


logging_level = {
    Level.INFO: logging.INFO,
    Level.WARNING: logging.WARNING,
    Level.DEBUG: logging.DEBUG,
    Level.ERROR: logging.ERROR,
    Level.CRITICAL: logging.CRITICAL,
}

logging_level_index = {
    Level.INFO: 4,
    Level.WARNING: 3,
    Level.DEBUG: 2,
    Level.ERROR: 1,
    Level.CRITICAL: 0,
}
