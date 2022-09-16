"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from enum import Enum

from sc_client.constants import sc_types

from sc_kpm.sc_keynodes import ScKeynodes


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


class _IdentifiersResolver:
    """
    Class for resolving common identifiers and question status identifiers.
    It confirms the presence of all of them in the KB.
    """

    is_resolved = False

    @classmethod
    def resolve(cls) -> None:
        if cls.is_resolved:
            return
        types_map = {
            CommonIdentifiers.QUESTION: sc_types.NODE_CONST_CLASS,
            CommonIdentifiers.EXACT_VALUE: sc_types.NODE_CONST_CLASS,
            CommonIdentifiers.RREL_DYNAMIC_ARGUMENT: sc_types.NODE_CONST_ROLE,
            CommonIdentifiers.RREL_ONE: sc_types.NODE_CONST_ROLE,
            CommonIdentifiers.RREL_TWO: sc_types.NODE_CONST_ROLE,
            CommonIdentifiers.NREL_BASIC_SEQUENCE: sc_types.NODE_CONST_NOROLE,
            CommonIdentifiers.NREL_SYSTEM_IDENTIFIER: sc_types.NODE_CONST_NOROLE,
            CommonIdentifiers.NREL_ANSWER: sc_types.NODE_CONST_NOROLE,
            CommonIdentifiers.CONCEPT_FILENAME: sc_types.NODE_CONST_CLASS,
            QuestionStatus.QUESTION_INITIATED: sc_types.NODE_CONST_CLASS,
            QuestionStatus.QUESTION_FINISHED: sc_types.NODE_CONST_CLASS,
            QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY: sc_types.NODE_CONST_CLASS,
            QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY: sc_types.NODE_CONST_CLASS,
        }

        keynodes = ScKeynodes()
        for idtf, sc_type in types_map.items():
            keynodes.resolve(idtf.value, sc_type)

        cls.is_resolved = True
