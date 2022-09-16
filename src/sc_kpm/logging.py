"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging

KPM_LOGGER_NAME = "py-sc-kpm"


def get_kpm_logger() -> logging.Logger:
    return logging.getLogger(KPM_LOGGER_NAME)
