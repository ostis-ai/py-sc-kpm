"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from enum import Enum


class ScResult(Enum):
    # SC_RESULT_ERROR should be 0 anytime
    SC_RESULT_ERROR = 0  # unknown error
    # SC_RESULT_OK should be 1 anytime
    SC_RESULT_OK = 1  # no any error
    SC_RESULT_ERROR_INVALID_PARAMS = 2  # invalid function parameters error
    SC_RESULT_ERROR_INVALID_TYPE = 3  # invalid type error
    SC_RESULT_ERROR_IO = 4  # input/output error
    SC_RESULT_ERROR_INVALID_STATE = 5  # invalid state of processed object
    SC_RESULT_ERROR_NOT_FOUND = 6  # item not found
    SC_RESULT_ERROR_NO_WRITE_RIGHTS = 7  # no rights to change or delete object
    SC_RESULT_ERROR_NO_READ_RIGHTS = 8  # no rights to read object
    SC_RESULT_NO = 9  # no any result
    SC_RESULT_UNKNOWN = 10  # result unknown
