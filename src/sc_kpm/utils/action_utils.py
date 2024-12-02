"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import warnings
from threading import Event
from typing import Dict, List, Tuple, Union

from sc_client import client
from sc_client.client import create_elementary_event_subscriptions, destroy_elementary_event_subscriptions
from sc_client.constants import sc_type
from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr, ScConstruction, ScEventSubscriptionParams, ScTemplate

from sc_kpm.identifiers import ActionStatus, CommonIdentifiers, ScAlias
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.sc_sets.sc_structure import ScStructure
from sc_kpm.utils.common_utils import (
    check_connector,
    generate_connector,
    generate_node,
    generate_non_role_relation,
    generate_role_relation,
    search_element_by_role_relation,
)

COMMON_WAIT_TIME: float = 5


def check_action_class(action_class: Union[ScAddr, Idtf], action_node: ScAddr) -> bool:
    action_class = ScKeynodes[action_class] if isinstance(action_class, Idtf) else action_class
    templ = ScTemplate()
    templ.triple(action_class, sc_type.VAR_PERM_POS_ARC, action_node)
    templ.triple(ScKeynodes[CommonIdentifiers.ACTION], sc_type.VAR_PERM_POS_ARC, action_node)
    search_results = client.search_by_template(templ)
    return len(search_results) > 0


def get_action_arguments(action_node: ScAddr, count: int) -> List[ScAddr]:
    arguments = []
    for index in range(1, count + 1):
        argument = search_element_by_role_relation(action_node, ScKeynodes.rrel_index(index))
        arguments.append(argument)
    return arguments


def generate_action_result(action_node: ScAddr, *elements: ScAddr) -> None:
    result_struct_node = ScStructure(*elements).set_node
    generate_non_role_relation(action_node, result_struct_node, ScKeynodes[CommonIdentifiers.NREL_RESULT])


def create_action_result(action_node: ScAddr, *elements: ScAddr) -> None:
    warnings.warn(
        "Action utils 'create_action_result' method is deprecated. Use `generate_action_result` method instead.",
        DeprecationWarning,
    )
    generate_action_result(action_node, *elements)


def get_action_result(action_node: ScAddr) -> ScAddr:
    templ = ScTemplate()
    templ.quintuple(
        action_node,
        sc_type.VAR_COMMON_ARC >> ScAlias.RELATION_ARC,
        sc_type.VAR_NODE_STRUCTURE >> ScAlias.ELEMENT,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes[CommonIdentifiers.NREL_RESULT],
    )
    if search_results := client.search_by_template(templ):
        return search_results[0].get(ScAlias.ELEMENT)
    return ScAddr(0)


IsDynamic = bool


def execute_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = ActionStatus.ACTION_INITIATED,
    reaction: Idtf = ActionStatus.ACTION_FINISHED_SUCCESSFULLY,
    wait_time: float = COMMON_WAIT_TIME,
) -> Tuple[ScAddr, bool]:
    action = call_agent(arguments, concepts, initiation)
    wait_agent(wait_time, action)
    result = check_connector(sc_type.VAR_PERM_POS_ARC, ScKeynodes[reaction], action)
    return action, result


def call_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = ActionStatus.ACTION_INITIATED,
) -> ScAddr:
    action = generate_action(*concepts)
    add_action_arguments(action, arguments)
    call_action(action, initiation)
    return action


def generate_action(*concepts: Idtf) -> ScAddr:
    construction = ScConstruction()
    construction.generate_node(sc_type.CONST_NODE, ScAlias.ACTION_NODE)
    for concept in concepts:
        construction.generate_connector(
            sc_type.CONST_PERM_POS_ARC,
            ScKeynodes.resolve(concept, sc_type.CONST_NODE_CLASS),
            ScAlias.ACTION_NODE,
        )
    action_node = client.generate_elements(construction)[0]
    return action_node


def create_action(*concepts: Idtf) -> ScAddr:
    warnings.warn(
        "Action utils 'create_action' method is deprecated. Use `generate_action` method instead.",
        DeprecationWarning,
    )
    return generate_action(*concepts)


def add_action_arguments(action_node: ScAddr, arguments: Dict[ScAddr, IsDynamic]) -> None:
    rrel_dynamic_arg = ScKeynodes[CommonIdentifiers.RREL_DYNAMIC_ARGUMENT]
    argument: ScAddr
    for index, (argument, is_dynamic) in enumerate(arguments.items(), 1):
        if argument.is_valid():
            rrel_i = ScKeynodes.rrel_index(index)
            if is_dynamic:
                dynamic_node = generate_node(sc_type.CONST_NODE)
                generate_role_relation(action_node, dynamic_node, rrel_dynamic_arg, rrel_i)
                generate_connector(sc_type.CONST_TEMP_POS_ARC, dynamic_node, argument)
            else:
                generate_role_relation(action_node, argument, rrel_i)


def execute_action(
    action_node: ScAddr,
    initiation: Idtf = ActionStatus.ACTION_INITIATED,
    reaction: Idtf = ActionStatus.ACTION_FINISHED_SUCCESSFULLY,
    wait_time: float = COMMON_WAIT_TIME,
) -> bool:
    call_action(action_node, initiation)
    wait_agent(wait_time, action_node)
    result = check_connector(sc_type.VAR_PERM_POS_ARC, ScKeynodes[reaction], action_node)
    return result


def call_action(action_node: ScAddr, initiation: Idtf = ActionStatus.ACTION_INITIATED) -> None:
    initiation_node = ScKeynodes.resolve(initiation, sc_type.CONST_NODE_CLASS)
    generate_connector(sc_type.CONST_PERM_POS_ARC, initiation_node, action_node)


def wait_agent(seconds: float, action_node: ScAddr, reaction_node: ScAddr = None) -> None:
    reaction_node = reaction_node or ScKeynodes[ActionStatus.ACTION_FINISHED]
    finish_event = Event()

    def event_callback(_: ScAddr, __: ScAddr, trg: ScAddr) -> ScResult:
        if trg != reaction_node:
            return ScResult.SKIP
        finish_event.set()
        return ScResult.OK

    event_params = ScEventSubscriptionParams(action_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, event_callback)
    sc_event = create_elementary_event_subscriptions(event_params)[0]
    if not check_connector(sc_type.VAR_PERM_POS_ARC, reaction_node, action_node):
        finish_event.wait(seconds)
    destroy_elementary_event_subscriptions(sc_event)
    # TODO: return status in 0.2.0


def finish_action(action_node: ScAddr, status: Idtf = ActionStatus.ACTION_FINISHED) -> ScAddr:
    return generate_connector(sc_type.CONST_PERM_POS_ARC, ScKeynodes[status], action_node)


def finish_action_with_status(action_node: ScAddr, is_success: bool = True) -> None:
    status = ActionStatus.ACTION_FINISHED_SUCCESSFULLY if is_success else ActionStatus.ACTION_FINISHED_UNSUCCESSFULLY
    finish_action(action_node, status)
    finish_action(action_node, ActionStatus.ACTION_FINISHED)
