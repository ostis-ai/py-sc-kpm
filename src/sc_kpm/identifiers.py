"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from enum import Enum

Idtf = str


class CommonIdentifiers(Enum):
    QUESTION = "question"
    EXACT_VALUE = "exact_value"
    RREL_DYNAMIC_ARGUMENT = "rrel_dynamic_argument"
    RREL_ONE = "rrel_1"
    RREL_TWO = "rrel_2"
    NREL_BASIC_SEQUENCE = "nrel_basic_sequence"
    NREL_SYSTEM_IDENTIFIER = "nrel_system_identifier"
    NREL_ANSWER = "nrel_answer"
    CONCEPT_FILENAME = "concept_filename"


class QuestionStatus(Enum):
    QUESTION_INITIATED = "question_initiated"
    QUESTION_FINISHED = "question_finished"
    QUESTION_FINISHED_SUCCESSFULLY = "question_finished_successfully"
    QUESTION_FINISHED_UNSUCCESSFULLY = "question_finished_unsuccessfully"


class ScAlias(Enum):
    ACTION_NODE = "_action_node"
    RELATION_EDGE = "_relation_edge"
    ACCESS_EDGE = "_access_edge"
    ELEMENT = "_element"
    LINK = "_link"
