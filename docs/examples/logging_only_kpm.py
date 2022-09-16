"""
Every logger in project has name <LOGGER_NAME='py-sc-kpm'>.
This code configures logging config that outputs only py-sc-kpm logs in console and logfile.

If you need see not only kpm logs in console, you can remove stream handler and configure basic config
"""

import logging.config
from pathlib import Path

from sc_kpm import KPM_LOGGER_NAME

logging.config.dictConfig(
    dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            "common_formatter": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "[%d-%b-%y %H:%M:%S]",
            }
        },
        handlers={
            "stream_handler": {
                "class": "logging.StreamHandler",
                "level": logging.INFO,
                "formatter": "common_formatter",
            },
            "file_handler": {
                "class": "logging.FileHandler",
                "level": logging.DEBUG,
                "filename": Path(__file__).resolve().parent.joinpath("py_sc_kpm.log"),
                "formatter": "common_formatter",
            },
        },
        loggers={
            KPM_LOGGER_NAME: {
                "handlers": ["stream_handler", "file_handler"],
                "level": logging.DEBUG,
            }
        },
    )
)
