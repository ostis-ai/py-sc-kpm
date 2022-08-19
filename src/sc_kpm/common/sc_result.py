"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from enum import Enum


class ScResult(Enum):
    # ScResult.ERROR should be 0 anytime
    ERROR = 0  # unknown error
    # ScResult.OK should be 1 anytime
    OK = 1  # no any error
    ERROR_INVALID_PARAMS = 2  # invalid function parameters error
    ERROR_INVALID_TYPE = 3  # invalid type error
    ERROR_IO = 4  # input/output error
    ERROR_INVALID_STATE = 5  # invalid state of processed object
    ERROR_NOT_FOUND = 6  # item not found
    ERROR_NO_WRITE_RIGHTS = 7  # no rights to change or delete object
    ERROR_NO_READ_RIGHTS = 8  # no rights to read object
    NO = 9  # no any result
    UNKNOWN = 10  # result unknown
