import logging.config
from typing import Optional

import constants as c


def get_logger(log_level: str,
               path_to_logs: Optional[str] = None,
               log_to_file_level: Optional[str] = None) -> logging.Logger:

    if path_to_logs is None and log_to_file_level is None:

        handlers = {
            c.CONSOLE_HANDLER: {"class": "logging.StreamHandler", "level": c.logging_level[log_level]}
        }
        handler_list = [c.CONSOLE_HANDLER]
        max_level = get_max_level(log_level= log_level)
    else:
        if path_to_logs is None:
            path_to_logs = "./logs.txt"
        if log_to_file_level is None:
            log_to_file_level = c.Level.DEBUG
        handlers = {
            c.CONSOLE_HANDLER: {"class": "logging.StreamHandler",
                                "level": c.logging_level[log_level]},
            c.TO_FILE_HANDLER: {"class": "logging.FileHandler",
                                "level": c.logging_level[log_to_file_level],
                                "filename": path_to_logs}
        }

        handler_list = [c.CONSOLE_HANDLER, c.TO_FILE_HANDLER]
        max_level = get_max_level(log_level= log_level, log_to_file_level= log_to_file_level)

    logging.config.dictConfig(
        dict(
            version=1,
            disable_existing_loggers=False,
            handlers=handlers,
            loggers={
                c.LOGGER: {"handlers": handler_list, "level": c.logging_level[max_level]}
            },
        )
    )
    logger = logging.getLogger(c.LOGGER)
    return logger


def get_max_level(log_level: str, log_to_file_level: Optional[str] = None) -> str:
    if log_to_file_level is None:
        return log_level
    elif c.logging_level_index[log_level] >= c.logging_level_index[log_to_file_level]:
        return log_level
    else:
        return log_to_file_level
