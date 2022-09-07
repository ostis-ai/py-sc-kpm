import logging.config
from dataclasses import dataclass


def logging_configurate() -> None:
    logging.config.dictConfig(
        dict(
            version=1,
            disable_existing_loggers=False,
            handlers={
                "info_handler": {"class": "logging.StreamHandler", "level": logging.INFO},
                "warning_handler": {"class": "logging.StreamHandler", "level": logging.WARNING},
                "debug_handler": {"class": "logging.StreamHandler", "level": logging.DEBUG},
                "error_handler": {"class": "logging.StreamHandler", "level": logging.ERROR},
                "critical_handler": {"class": "logging.StreamHandler", "level": logging.CRITICAL},
                "info_file_handler": {"class": "logging.handlers.RotatingFileHandler",
                                      "level": logging.INFO},
                "warning_file_handler": {"class": "logging.handlers.RotatingFileHandler",
                                         "level": logging.WARNING},
                "debug_file_handler": {"class": "logging.handlers.RotatingFileHandler",
                                       "level": logging.DEBUG},
                "error_file_handler": {"class": "logging.handlers.RotatingFileHandler",
                                       "level": logging.ERROR},
                "critical_file_handler": {"class": "logging.handlers.RotatingFileHandler",
                                          "level": logging.CRITICAL},
            },
            loggers={
                "info": {"handlers": ["info_handler"], "level": logging.INFO},
                "warning": {"handlers": ["warning_handler"], "level": logging.WARNING},
                "debug": {"handlers": ["debug_handler"], "level": logging.DEBUG},
                "error": {"handlers": ["error_handler"], "level": logging.ERROR},
                "critical": {"handlers": ["critical_handler"], "level": logging.CRITICAL},
            },
        )
    )


@dataclass(frozen=True)
class Loggers:
    INFO: str = "info"
    WARNING: str = "warning"
    DEBUG: str = "debug"
    ERROR: str = "error"
    CRITICAL: str = "critical"


@dataclass(frozen=True)
class Handlers:
    INFO_TO_FILE: str = "info_file_handler"
    WARNING_TO_FILE: str = "warning_file_handler"
    DEBUG_TO_FILE: str = "debug_file_handler"
    ERROR_TO_FILE: str = "error_file_handler"
    CRITICAL_TO_FILE: str = "critical_file_handler"
