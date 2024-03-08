"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import time

from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.core.asc_client_instance import asc_client
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm import AScAgent, AScModule
from asc_kpm.asc_keynodes_ import asc_keynodes
from asc_kpm.utils.aio_action_utils import (
    add_action_arguments,
    call_action,
    call_agent,
    check_action_class,
    create_action,
    execute_action,
    execute_agent,
    finish_action_with_status,
    wait_agent,
)
from asc_kpm.utils.aio_common_utils import check_edge, create_edge, create_node
from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus
from sc_kpm.sc_result import ScResult

test_node_idtf = "test_node"


class AScAgentTest(AScAgent):
    async def on_event(self, _src, _edge, target_node) -> ScResult:
        self.logger.info(f"Agent's started")
        await finish_action_with_status(target_node)
        return ScResult.OK


class AScModuleTest(AScModule):
    @classmethod
    async def ainit(cls):
        return await super().ainit(
            await AScAgentTest.ainit(test_node_idtf, ScEventType.ADD_OUTGOING_EDGE),
            await AScAgentTest.ainit(test_node_idtf, ScEventType.ADD_INGOING_EDGE),
        )


class TestActionUtils(AsyncioScKpmTestCase):
    async def test_validate_action(self):
        action_class_idtf = "test_action_class"
        action_class_node = await asc_keynodes.resolve(action_class_idtf, sc_types.NODE_CONST)
        question = await asc_keynodes.get_valid(CommonIdentifiers.QUESTION)
        test_node = await create_node(sc_types.NODE_CONST)
        self.assertFalse(await check_action_class(action_class_node, test_node))
        self.assertFalse(await check_action_class(action_class_idtf, test_node))
        class_edge = await create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, action_class_node, test_node)
        self.assertFalse(await check_action_class(action_class_node, test_node))
        self.assertFalse(await check_action_class(action_class_idtf, test_node))
        await create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, question, test_node)
        self.assertTrue(await check_action_class(action_class_node, test_node))
        self.assertTrue(await check_action_class(action_class_idtf, test_node))
        await asc_client.delete_elements(class_edge)
        self.assertFalse(await check_action_class(action_class_node, test_node))
        self.assertFalse(await check_action_class(action_class_idtf, test_node))

    async def test_execute_agent(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            results = await execute_agent({}, [], test_node_idtf)
            assert results[1]
        await self.server.remove_modules(module)

    async def test_call_agent(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            question = await call_agent({}, [], test_node_idtf)
            await wait_agent(1, question, await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED))
            result = await check_edge(
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY),
                question,
            )
            self.assertTrue(result)
        await self.server.remove_modules(module)

    async def test_wrong_execute_agent(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            self.assertFalse((await execute_agent({}, [], "wrong_agent", wait_time=1))[1])
        await self.server.remove_modules(module)

    async def test_execute_action(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            action_node = await create_action()
            await add_action_arguments(action_node, {})
            assert await execute_action(action_node, test_node_idtf)
        await self.server.remove_modules(module)

    async def test_call_action(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            action_node = await create_action()
            await add_action_arguments(action_node, {})
            await call_action(action_node, test_node_idtf)
            await wait_agent(1, action_node, await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED))
            result = await check_edge(
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY),
                action_node,
            )
            self.assertTrue(result)
        await self.server.remove_modules(module)

    async def test_wrong_execute_action(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            action_node = await create_action()
            await add_action_arguments(action_node, {})
            self.assertFalse(await execute_action(action_node, "wrong_agent", wait_time=1))
        await self.server.remove_modules(module)

    async def test_wait_action(self):
        module = await AScModuleTest.ainit()
        await self.server.add_modules(module)
        async with self.server.register_modules():
            action_node = await create_action()
            timeout = 0.5
            # Action is not finished while waiting
            start_time = time.time()
            await wait_agent(timeout, action_node, await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED))
            timedelta = time.time() - start_time
            self.assertGreater(timedelta, timeout)
            # Action is finished while waiting
            await call_action(action_node, test_node_idtf)
            start_time = time.time()
            await wait_agent(timeout, action_node, await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED))
            timedelta = time.time() - start_time
            self.assertLess(timedelta, timeout)
            # Action finished before waiting
            await call_action(action_node, test_node_idtf)
            time.sleep(0.1)
            start_time = time.time()
            await wait_agent(timeout, action_node, await asc_keynodes.get_valid(QuestionStatus.QUESTION_FINISHED))
            timedelta = time.time() - start_time
            self.assertLess(timedelta, timeout)
        await self.server.remove_modules(module)
