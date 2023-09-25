"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import asyncio
from asyncio import Future
from typing import Dict, List, Tuple, Union

from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import AScEventParams, ScAddr, ScConstruction, ScTemplate

from asc_kpm.asc_keynodes_ import Idtf, asc_keynodes
from asc_kpm.asc_sets import AScStructure
from asc_kpm.utils.aio_common_utils import (
    check_edge,
    create_edge,
    create_node,
    create_norole_relation,
    create_role_relation,
    get_element_by_role_relation,
)
from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus, ScAlias

COMMON_WAIT_TIME: float = 5


async def check_action_class(action_class: Union[ScAddr, Idtf], action_node: ScAddr) -> bool:
    action_class = await asc_keynodes.get_valid(action_class) if isinstance(action_class, Idtf) else action_class
    templ = ScTemplate()
    templ.triple(action_class, sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node)
    templ.triple(
        await asc_keynodes.get_valid(CommonIdentifiers.QUESTION), sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node
    )
    search_results = await asc_client.template_search(templ)
    return len(search_results) > 0


async def get_action_arguments(action_node: ScAddr, count: int) -> List[ScAddr]:
    arguments = []
    for index in range(1, count + 1):
        argument = await get_element_by_role_relation(action_node, await asc_keynodes.rrel_index(index))
        arguments.append(argument)
    return arguments


async def create_action_answer(action_node: ScAddr, *elements: ScAddr) -> None:
    asc_structure = await AScStructure.create(*elements)
    answer_struct_node = asc_structure.set_node
    await create_norole_relation(
        action_node, answer_struct_node, await asc_keynodes.get_valid(CommonIdentifiers.NREL_ANSWER)
    )


async def get_action_answer(action_node: ScAddr) -> ScAddr:
    templ = ScTemplate()
    templ.triple_with_relation(
        action_node,
        sc_types.EDGE_D_COMMON_VAR >> ScAlias.RELATION_EDGE,
        sc_types.NODE_VAR_STRUCT >> ScAlias.ELEMENT,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        await asc_keynodes.get_valid(CommonIdentifiers.NREL_ANSWER),
    )
    if search_results := await asc_client.template_search(templ):
        return search_results[0].get(ScAlias.ELEMENT)
    return ScAddr(0)


IsDynamic = bool


async def execute_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED,
    reaction: Idtf = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
    wait_time: float = COMMON_WAIT_TIME,
) -> Tuple[ScAddr, bool]:
    question = await call_agent(arguments, concepts, initiation)
    await wait_agent(wait_time, question)
    result = await check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, await asc_keynodes.get_valid(reaction), question)
    return question, result


async def call_agent(
    arguments: Dict[ScAddr, IsDynamic],
    concepts: List[Idtf],
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED,
) -> ScAddr:
    question = await create_action(*concepts)
    await add_action_arguments(question, arguments)
    await call_action(question, initiation)
    return question


async def create_action(*concepts: Idtf) -> ScAddr:
    construction = ScConstruction()
    construction.create_node(sc_types.NODE_CONST, ScAlias.ACTION_NODE)
    for concept in concepts:
        construction.create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            await asc_keynodes.resolve(concept, sc_types.NODE_CONST_CLASS),
            ScAlias.ACTION_NODE,
        )
    action_node = (await asc_client.create_elements(construction))[0]
    return action_node


async def add_action_arguments(action_node: ScAddr, arguments: Dict[ScAddr, IsDynamic]) -> None:
    rrel_dynamic_arg = await asc_keynodes.get_valid(CommonIdentifiers.RREL_DYNAMIC_ARGUMENT)
    index: int
    argument: ScAddr
    for index, (argument, is_dynamic) in enumerate(arguments.items(), 1):
        if argument.is_valid():
            rrel_i = await asc_keynodes.rrel_index(index)
            if is_dynamic:
                dynamic_node = await create_node(sc_types.NODE_CONST)
                await create_role_relation(action_node, dynamic_node, rrel_dynamic_arg, rrel_i)
                await create_edge(sc_types.EDGE_ACCESS_CONST_POS_TEMP, dynamic_node, argument)
            else:
                await create_role_relation(action_node, argument, rrel_i)


async def execute_action(
    action_node: ScAddr,
    initiation: Idtf = QuestionStatus.QUESTION_INITIATED,
    reaction: Idtf = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
    wait_time: float = COMMON_WAIT_TIME,
) -> bool:
    await call_action(action_node, initiation)
    await wait_agent(wait_time, action_node)
    result = await check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, await asc_keynodes.get_valid(reaction), action_node)
    return result


async def call_action(action_node: ScAddr, initiation: Idtf = QuestionStatus.QUESTION_INITIATED) -> None:
    initiation_node = await asc_keynodes.resolve(initiation, sc_types.NODE_CONST_CLASS)
    await create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, initiation_node, action_node)


async def wait_agent(seconds: float, question_node: ScAddr, reaction_node: ScAddr = None) -> None:
    reaction_node = reaction_node or await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED)
    finish_future = Future()

    async def event_callback(_: ScAddr, __: ScAddr, trg: ScAddr) -> None:
        if trg != reaction_node:
            return
        finish_future.set_result(True)

    async def timer():
        await asyncio.sleep(seconds)
        finish_future.set_result(False)

    asyncio.create_task(timer())
    event_params = AScEventParams(question_node, ScEventType.ADD_INGOING_EDGE, event_callback)
    sc_event = (await asc_client.events_create(event_params))[0]
    if not await check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, reaction_node, question_node):
        await finish_future
    await asc_client.events_destroy(sc_event)
    # TODO: return status in 0.2.0


async def finish_action(action_node: ScAddr, status: Idtf = QuestionStatus.QUESTION_FINISHED) -> ScAddr:
    return await create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, await asc_keynodes.get_valid(status), action_node)


async def finish_action_with_status(action_node: ScAddr, is_success: bool = True) -> None:
    status = (
        QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY if is_success else QuestionStatus.QUESTION_FINISHED_UNSUCCESSFULLY
    )
    await finish_action(action_node, status)
    await finish_action(action_node, QuestionStatus.QUESTION_FINISHED)
