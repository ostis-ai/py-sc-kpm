"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

import time
from datetime import datetime
from typing import Dict, List

import dateutil.parser
from sc_client import client
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate, ScConstruction

from sc_common.identifiers import CommonIdentifiers, QuestionStatus
from sc_common.sc_keynodes import ScKeynodes
from sc_utils.constants import COMMON_WAIT_TIME, RREL_PREFIX, ScAlias
from sc_utils.generator import generate_edge, generate_node, generate_binary_relation
from sc_utils.searcher import check_edge

Idtf = str


def validate_action(source: Idtf, target: ScAddr) -> bool:
    keynodes = ScKeynodes()
    templ = ScTemplate()
    templ.triple(keynodes[source], sc_types.EDGE_ACCESS_VAR_POS_PERM, target)
    templ.triple(keynodes[CommonIdentifiers.QUESTION.value], sc_types.EDGE_ACCESS_VAR_POS_PERM, target)
    search_results = client.template_search(templ)
    return len(search_results) > 0


def call_agent(
    arguments: Dict[ScAddr, bool],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED.value,
    reaction: QuestionStatus = QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY,
    wait_time: int = COMMON_WAIT_TIME,
) -> bool:
    keynodes = ScKeynodes()
    question = call_agent_without_waiting(arguments, concepts, initiation)
    wait_agent(wait_time, question, keynodes[QuestionStatus.QUESTION_FINISHED.value])
    result = check_edge(keynodes[reaction.value], question, sc_types.EDGE_ACCESS_VAR_POS_PERM)
    return result


def call_agent_without_waiting(
    arguments: Dict[ScAddr, bool],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED.value,
) -> ScAddr:
    keynodes = ScKeynodes()
    question = generate_action_with_arguments(arguments, concepts)
    generate_edge(
        keynodes[initiation],
        question,
        sc_types.EDGE_ACCESS_CONST_POS_PERM,
    )
    return question


def generate_action_with_arguments(arguments: Dict[ScAddr, bool], concepts: List[Idtf]) -> ScAddr:
    action = generate_action(concepts)
    keynodes = ScKeynodes()

    for index, argument in enumerate(arguments, 1):
        if argument.is_valid():
            rrel_identifier = f"{RREL_PREFIX}{index}"
            is_dynamic = arguments[argument]
            if is_dynamic:
                variable = generate_node(sc_types.NODE_CONST)
                generate_binary_relation(
                    action,
                    sc_types.EDGE_ACCESS_CONST_POS_PERM,
                    variable,
                    keynodes[CommonIdentifiers.RREL_DYNAMIC_ARGUMENT.value],
                    keynodes[rrel_identifier],
                )
                generate_edge(variable, argument, sc_types.EDGE_ACCESS_CONST_POS_TEMP)
            else:
                generate_binary_relation(
                    action, sc_types.EDGE_ACCESS_CONST_POS_PERM, argument, keynodes[rrel_identifier]
                )
    return action


def generate_action(concepts: List[Idtf]) -> ScAddr:
    keynodes = ScKeynodes()
    construction = ScConstruction()
    construction.create_node(sc_types.NODE_CONST, ScAlias.ACTION_NODE.value)
    for concept in concepts:
        construction.create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            keynodes.__getitem__(concept, sc_types.NODE_CONST_CLASS),
            ScAlias.ACTION_NODE.value,
        )
    addr_list = client.create_elements(construction)
    return addr_list[0]


def wait_agent(seconds: int, question_node: ScAddr, reaction_node: ScAddr):
    start = datetime.now()
    delta = 0
    while not check_edge(reaction_node, question_node, sc_types.EDGE_ACCESS_VAR_POS_PERM) and delta < seconds:
        delta = (datetime.now() - start).seconds
        time.sleep(0.1)


def finish_action(action_node: ScAddr, idtf: QuestionStatus = None) -> ScAddr:
    keynodes = ScKeynodes()
    idtf = idtf if idtf else QuestionStatus.QUESTION_FINISHED
    return generate_edge(
        keynodes[idtf.value],
        action_node,
        sc_types.EDGE_ACCESS_CONST_POS_PERM,
    )


def finish_action_status(action_node: ScAddr, status: bool = True) -> None:
    finish_action(
        action_node,
        QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY if status else QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY,
    )
    finish_action(action_node, QuestionStatus.QUESTION_FINISHED)


def convert_timestamp_format(timestamp: str, timestamp_format: str) -> str:
    try:
        iso_timestamp_format = dateutil.parser.parse(timestamp).isoformat()
        return dateutil.parser.isoparse(iso_timestamp_format).strftime(timestamp_format)
    except ValueError:
        return ""
