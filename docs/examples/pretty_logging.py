"""
Every logger in project has name <LOGGER_NAME='py-sc-kpm'>.
This code configures logging config that outputs only py-sc-kpm logs in console and logfile.

If you need see not only kpm logs in console, you can remove stream handler and configure basic config
"""

import logging.config
from pathlib import Path

PROJECT_NAME = __name__

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "common_formatter": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "[%d-%b-%y %H:%M:%S]",
            }
        },
        "handlers": {
            "stream_handler": {
                "class": "logging.StreamHandler",
                "level": logging.DEBUG,
                "formatter": "common_formatter",
            },
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1_000_000,
                "backupCount": 3,
                "level": logging.DEBUG,
                "filename": Path(__file__).resolve().parent.joinpath("root.log"),
                "formatter": "common_formatter",
            },
        },
        "root": {
            "handlers": ["file_handler"],
            "level": logging.DEBUG,
        },
        "loggers": {
            PROJECT_NAME: {
                "handlers": ["stream_handler"],
                "level": logging.INFO,
            },
        },
    }
)
