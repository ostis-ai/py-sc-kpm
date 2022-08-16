import time
from datetime import datetime
from typing import Dict, List, Union

from sc_client import client
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScConstruction, ScTemplate

from sc_kpm import ScKeynodes
from sc_kpm.common import CommonIdentifiers, QuestionStatus, ScAlias
from sc_kpm.utils.common_utils import check_edge, generate_edge, generate_node, generate_role_relation
from sc_kpm.utils.search_utils import get_first_search_template_result

Idtf = str
COMMON_WAIT_TIME = 5
RREL_PREFIX = "rrel_"


def validate_action(action_class: Union[ScAddr, Idtf], action_node: ScAddr) -> bool:
    keynodes = ScKeynodes()
    action_class = keynodes[action_class] if isinstance(action_class, Idtf) else action_class
    templ = ScTemplate()
    templ.triple(action_class, sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    templ.triple(keynodes[CommonIdentifiers.QUESTION.value], sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    search_results = client.template_search(templ)
    return len(search_results) > 0


def get_action_answer(action: ScAddr) -> ScAddr:
    templ = ScTemplate()
    keynodes = ScKeynodes()
    templ.triple_with_relation(
        action,
        [sc_types.EDGE_D_COMMON_VAR, ScAlias.RELATION_EDGE.value],
        [sc_types.NODE_VAR_STRUCT, ScAlias.ELEMENT.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes[CommonIdentifiers.NREL_ANSWER.value],
    )
    result = get_first_search_template_result(templ)
    return result.get(ScAlias.ELEMENT.value) if result else ScAddr(0)


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
    result = check_edge(keynodes[reaction.value], sc_types.EDGE_ACCESS_VAR_POS_PERM, question)
    return result


def call_agent_without_waiting(
    arguments: Dict[ScAddr, bool],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED.value,
) -> ScAddr:
    keynodes = ScKeynodes()
    question = generate_action_with_arguments(arguments, concepts)
    generate_edge(keynodes[initiation], sc_types.EDGE_ACCESS_CONST_POS_PERM, question)
    return question


def generate_action_with_arguments(arguments: Dict[ScAddr, bool], concepts: List[Idtf]) -> ScAddr:
    action = generate_action(concepts)
    keynodes = ScKeynodes()
    rrel_dynamic_arg = keynodes[CommonIdentifiers.RREL_DYNAMIC_ARGUMENT.value]

    for index, argument in enumerate(arguments, 1):
        if argument.is_valid():
            rrel_idtf = keynodes[f"{RREL_PREFIX}{index}"]
            is_dynamic = arguments[argument]
            if is_dynamic:
                variable = generate_node(sc_types.NODE_CONST)
                generate_role_relation(action, variable, rrel_dynamic_arg, rrel_idtf)
                generate_edge(variable, sc_types.EDGE_ACCESS_CONST_POS_TEMP, argument)
            else:
                generate_role_relation(action, argument, rrel_idtf)
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


# TODO rewrite to event
def wait_agent(seconds: int, question_node: ScAddr, reaction_node: ScAddr):
    start = datetime.now()
    delta = 0
    while not check_edge(reaction_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, question_node) and delta < seconds:
        delta = (datetime.now() - start).seconds
        time.sleep(0.1)


def finish_action(action_node: ScAddr, status: QuestionStatus = None) -> ScAddr:
    keynodes = ScKeynodes()
    status = status if status else QuestionStatus.QUESTION_FINISHED
    return generate_edge(keynodes[status.value], sc_types.EDGE_ACCESS_CONST_POS_PERM, action_node)


def finish_action_with_status(action_node: ScAddr, is_success: bool = True) -> None:
    if is_success:
        status_node = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY
    else:
        status_node = QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY
    finish_action(action_node, status_node)
    finish_action(action_node, QuestionStatus.QUESTION_FINISHED)
