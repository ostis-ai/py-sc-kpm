"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union

from sc_client import client
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScConstruction, ScTemplate

from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus, ScAlias
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.utils.common_utils import check_edge, create_edge, create_node, create_role_relation
from sc_kpm.utils.retrieve_utils import _get_first_search_template_result

COMMON_WAIT_TIME: int = 5


def check_action_class(action_class: Union[ScAddr, Idtf], action_node: ScAddr) -> bool:
    keynodes = ScKeynodes()
    action_class = keynodes[action_class] if isinstance(action_class, Idtf) else action_class
    templ = ScTemplate()
    templ.triple(action_class, sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    templ.triple(keynodes[CommonIdentifiers.QUESTION.value], sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    search_results = client.template_search(templ)
    return len(search_results) > 0


def get_action_answer(action_node: ScAddr) -> ScAddr:
    keynodes = ScKeynodes()
    templ = ScTemplate()
    templ.triple_with_relation(
        action_node,
        [sc_types.EDGE_D_COMMON_VAR, ScAlias.RELATION_EDGE.value],
        [sc_types.NODE_VAR_STRUCT, ScAlias.ELEMENT.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes[CommonIdentifiers.NREL_ANSWER.value],
    )
    result = _get_first_search_template_result(templ)
    return result.get(ScAlias.ELEMENT.value) if result else ScAddr(0)


IsDynamic = bool


def execute_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED.value,
    reaction: QuestionStatus = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
    wait_time: int = COMMON_WAIT_TIME,
) -> Tuple[ScAddr, bool]:
    keynodes = ScKeynodes()
    question = call_agent(arguments, concepts, initiation)
    wait_agent(wait_time, question, keynodes[QuestionStatus.QUESTION_FINISHED.value])
    result = check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, keynodes[reaction.value], question)
    return question, result


def call_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED.value,
) -> ScAddr:
    keynodes = ScKeynodes()
    question = _create_action_with_arguments(arguments, concepts)
    create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynodes[initiation], question)
    return question


def _create_action_with_arguments(arguments: Dict[ScAddr, IsDynamic], concepts: List[Idtf]) -> ScAddr:
    action_node = _create_action(concepts)
    keynodes = ScKeynodes()
    rrel_dynamic_arg = keynodes[CommonIdentifiers.RREL_DYNAMIC_ARGUMENT.value]

    argument: ScAddr
    for index, (argument, is_dynamic) in enumerate(arguments.items(), 1):
        if argument.is_valid():
            rrel_i = keynodes[f"rrel_{index}"]
            if is_dynamic:
                dynamic_node = create_node(sc_types.NODE_CONST)
                create_role_relation(action_node, dynamic_node, rrel_dynamic_arg, rrel_i)
                create_edge(sc_types.EDGE_ACCESS_CONST_POS_TEMP, dynamic_node, argument)
            else:
                create_role_relation(action_node, argument, rrel_i)
    return action_node


def _create_action(concepts: List[Idtf]) -> ScAddr:
    keynodes = ScKeynodes()
    construction = ScConstruction()
    construction.create_node(sc_types.NODE_CONST, ScAlias.ACTION_NODE.value)
    for concept in concepts:
        construction.create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            keynodes.resolve(concept, sc_types.NODE_CONST_CLASS),
            ScAlias.ACTION_NODE.value,
        )
    action_node = client.create_elements(construction)[0]
    return action_node


# TODO rewrite to event
def wait_agent(seconds: int, question_node: ScAddr, reaction_node: ScAddr):
    finish = datetime.now() + timedelta(seconds=seconds)
    while not check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, reaction_node, question_node) and datetime.now() < finish:
        time.sleep(0.1)


def finish_action(action_node: ScAddr, status: QuestionStatus = QuestionStatus.QUESTION_FINISHED) -> ScAddr:
    return create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, ScKeynodes()[status.value], action_node)


def finish_action_with_status(action_node: ScAddr, is_success: bool = True) -> None:
    finish_action(action_node, QuestionStatus.QUESTION_FINISHED)
    finish_action(
        action_node,
        QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY
        if is_success
        else QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY,
    )
