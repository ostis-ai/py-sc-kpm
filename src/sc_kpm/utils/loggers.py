import logging.config
from dataclasses import dataclass


def logging_configurate():
    logging.config.dictConfig(
        dict(
            version=1,
            disable_existing_loggers=False,
            handlers={
                "info_handler": {"class": "logging.StreamHandler", "level": logging.INFO},
                "warning_handler": {"class": "logging.StreamHandler", "level": logging.WARNING},
                "debug_handler": {"class": "logging.StreamHandler", "level": logging.DEBUG},
            },
            loggers={
                "info": {"handlers": ["info_handler"], "level": logging.INFO},
                "warning": {"handlers": ["warning_handler"], "level": logging.WARNING},
                "debug": {"handlers": ["debug_handler"], "level": logging.DEBUG},
            },
        )
    )


@dataclass(frozen=True)
class Loggers:
    INFO: str = "info"
    WARNING: str = "warning"
    DEBUG: str = "debug"
