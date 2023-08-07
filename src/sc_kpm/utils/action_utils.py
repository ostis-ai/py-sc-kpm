"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from threading import Event
from typing import Dict, List, Tuple, Union

from sc_client import ScAddr, sc_client, sc_keynodes
from sc_client._sc_keynodes import Idtf
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.models import ScConstruction, ScEventParams, ScTemplate
from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus, ScAlias
from sc_kpm.sc_result import ScResult
from sc_kpm.sc_sets.sc_structure import ScStructure
from sc_kpm.utils.common_utils import (
    check_edge,
    create_edge,
    create_node,
    create_norole_relation,
    create_role_relation,
    get_element_by_role_relation,
)

COMMON_WAIT_TIME: float = 5


def check_action_class(action_class: Union[ScAddr, Idtf], action_node: ScAddr) -> bool:
    action_class = sc_keynodes[action_class] if isinstance(action_class, Idtf) else action_class
    templ = ScTemplate()
    templ.triple(action_class, sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    templ.triple(sc_keynodes[CommonIdentifiers.QUESTION], sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    search_results = sc_client.template_search(templ)
    return len(search_results) > 0


def get_action_arguments(action_node: ScAddr, count: int) -> List[ScAddr]:
    arguments = []
    for index in range(1, count + 1):
        argument = get_element_by_role_relation(action_node, sc_keynodes.rrel_index(index))
        arguments.append(argument)
    return arguments


def create_action_answer(action_node: ScAddr, *elements: ScAddr) -> None:
    answer_struct_node = ScStructure(*elements).set_node
    create_norole_relation(action_node, answer_struct_node, sc_keynodes[CommonIdentifiers.NREL_ANSWER])


def get_action_answer(action_node: ScAddr) -> ScAddr:
    templ = ScTemplate()
    templ.triple_with_relation(
        action_node,
        sc_types.EDGE_D_COMMON_VAR >> ScAlias.RELATION_EDGE,
        sc_types.NODE_VAR_STRUCT >> ScAlias.ELEMENT,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        sc_keynodes[CommonIdentifiers.NREL_ANSWER],
    )
    if search_results := sc_client.template_search(templ):
        return search_results[0].get(ScAlias.ELEMENT)
    return ScAddr(0)


IsDynamic = bool


def execute_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED,
    reaction: Idtf = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
    wait_time: float = COMMON_WAIT_TIME,
) -> Tuple[ScAddr, bool]:
    question = call_agent(arguments, concepts, initiation)
    wait_agent(wait_time, question)
    result = check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_keynodes[reaction], question)
    return question, result


def call_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED,
) -> ScAddr:
    question = create_action(*concepts)
    add_action_arguments(question, arguments)
    call_action(question, initiation)
    return question


def create_action(*concepts: Idtf) -> ScAddr:
    construction = ScConstruction()
    construction.create_node(sc_types.NODE_CONST, ScAlias.ACTION_NODE)
    for concept in concepts:
        construction.create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            sc_keynodes.resolve(concept, sc_types.NODE_CONST_CLASS),
            ScAlias.ACTION_NODE,
        )
    action_node = sc_client.create_elements(construction)[0]
    return action_node


def add_action_arguments(action_node: ScAddr, arguments: Dict[ScAddr, IsDynamic]) -> None:
    rrel_dynamic_arg = sc_keynodes[CommonIdentifiers.RREL_DYNAMIC_ARGUMENT]
    argument: ScAddr
    for index, (argument, is_dynamic) in enumerate(arguments.items(), 1):
        if argument.is_valid():
            rrel_i = sc_keynodes.rrel_index(index)
            if is_dynamic:
                dynamic_node = create_node(sc_types.NODE_CONST)
                create_role_relation(action_node, dynamic_node, rrel_dynamic_arg, rrel_i)
                create_edge(sc_types.EDGE_ACCESS_CONST_POS_TEMP, dynamic_node, argument)
            else:
                create_role_relation(action_node, argument, rrel_i)


def execute_action(
    action_node: ScAddr,
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED,
    reaction: Idtf = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
    wait_time: float = COMMON_WAIT_TIME,
) -> bool:
    call_action(action_node, initiation)
    wait_agent(wait_time, action_node)
    result = check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_keynodes[reaction], action_node)
    return result


def call_action(action_node: ScAddr, initiation: Idtf = QuestionStatus.QUESTION_INITIATED) -> None:
    initiation_node = sc_keynodes.resolve(initiation, sc_types.NODE_CONST_CLASS)
    create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, initiation_node, action_node)


def wait_agent(seconds: float, question_node: ScAddr, reaction_node: ScAddr = None) -> None:
    reaction_node = reaction_node or sc_keynodes[QuestionStatus.QUESTION_FINISHED]
    finish_event = Event()

    def event_callback(_: ScAddr, __: ScAddr, trg: ScAddr) -> ScResult:
        if trg != reaction_node:
            return ScResult.SKIP
        finish_event.set()
        return ScResult.OK

    event_params = ScEventParams(question_node, ScEventType.ADD_INGOING_EDGE, event_callback)
    sc_event = sc_client.events_create(event_params)[0]
    if not check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, reaction_node, question_node):
        finish_event.wait(seconds)
    sc_client.events_destroy(sc_event)
    # TODO: return status in 0.2.0


def finish_action(action_node: ScAddr, status: Idtf = QuestionStatus.QUESTION_FINISHED) -> ScAddr:
    return create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, sc_keynodes[status], action_node)


def finish_action_with_status(action_node: ScAddr, is_success: bool = True) -> None:
    status = (
        QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY if is_success else QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY
    )
    finish_action(action_node, status)
    finish_action(action_node, QuestionStatus.QUESTION_FINISHED)
