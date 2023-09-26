"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import asyncio

from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.asc_agent import AScAgent, AScAgentClassic
from asc_kpm.asc_module import AScModule
from asc_kpm.utils.aio_action_utils import execute_agent, finish_action_with_status
from sc_kpm import ScResult
from sc_kpm.identifiers import CommonIdentifiers

WAIT_TIME = 1


class CommonTests(AsyncioScKpmTestCase):
    async def test_sc_agents(self):
        class Agent(AScAgent):
            ACTION_CLASS_NAME = "test_agent"

            @classmethod
            async def ainit(cls, **kwargs):
                return await super().ainit(cls.ACTION_CLASS_NAME, ScEventType.ADD_OUTGOING_EDGE)

            async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                await finish_action_with_status(action_element, True)
                return ScResult.OK

        class AgentClassic(AScAgentClassic):
            ACTION_CLASS_NAME = "test_agent_classic"

            @classmethod
            async def ainit(cls, **kwargs):
                return await super().ainit(cls.ACTION_CLASS_NAME)

            async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                await finish_action_with_status(action_element, True)
                return ScResult.OK

        module = await AScModule.ainit(await Agent.ainit(), await AgentClassic.ainit())
        await self.server.add_modules(module)
        arguments = dict(
            arguments={},
            concepts=[],
            initiation=Agent.ACTION_CLASS_NAME,
            wait_time=WAIT_TIME,
        )
        arguments_classic = dict(
            arguments={},
            concepts=[CommonIdentifiers.QUESTION, AgentClassic.ACTION_CLASS_NAME],
            wait_time=WAIT_TIME,
        )
        self.assertFalse((await execute_agent(**arguments))[1])
        self.assertFalse((await execute_agent(**arguments_classic))[1])
        async with self.server.register_modules():
            self.assertTrue((await execute_agent(**arguments))[1])
            self.assertTrue((await execute_agent(**arguments_classic))[1])
        self.assertFalse((await execute_agent(**arguments))[1])
        self.assertFalse((await execute_agent(**arguments_classic))[1])
        await self.server.remove_modules(module)

    async def test_sc_module(self):
        class TestAgent(AScAgent):
            async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                await finish_action_with_status(action_element, True)
                return ScResult.OK

        async def is_executing_successful(i: int) -> bool:
            return (
                await execute_agent(
                    arguments={},
                    concepts=[],
                    initiation=f"agent{i}",
                    wait_time=WAIT_TIME,
                )
            )[1]

        agent1 = await TestAgent.ainit("agent1", ScEventType.ADD_OUTGOING_EDGE)
        agent2 = await TestAgent.ainit("agent2", ScEventType.ADD_OUTGOING_EDGE)
        agent3 = await TestAgent.ainit("agent3", ScEventType.ADD_OUTGOING_EDGE)

        module1 = await AScModule.ainit(agent1)
        module2 = await AScModule.ainit(agent2)
        await self.server.add_modules(module1)
        await module1.add_agent(agent3)
        async with self.server.register_modules():
            self.assertTrue(await is_executing_successful(1))
            self.assertFalse(await is_executing_successful(2))
            self.assertTrue(await is_executing_successful(3))

            await self.server.add_modules(module2)
            self.assertTrue(await is_executing_successful(2))

            await module1.remove_agent(agent3)
            self.assertTrue(await is_executing_successful(1))
            self.assertFalse(await is_executing_successful(3))
            await self.server.remove_modules(module1, module2)

    async def test_sc_server(self):
        class TestAgent(AScAgent):
            ACTION_CLASS_NAME = "some_agent"

            @classmethod
            async def ainit(cls, **kwargs):
                return await super().ainit(cls.ACTION_CLASS_NAME, ScEventType.ADD_OUTGOING_EDGE)

            async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                await finish_action_with_status(action_element, True)
                return ScResult.OK

        async def is_executing_successful() -> bool:
            return (
                await execute_agent(
                    arguments={},
                    concepts=[],
                    initiation=TestAgent.ACTION_CLASS_NAME,
                    wait_time=WAIT_TIME,
                )
            )[1]

        module = await AScModule.ainit(await TestAgent.ainit())
        await self.server.add_modules(module)
        self.assertFalse(await is_executing_successful())
        await self.server.register_modules()
        self.assertTrue(await is_executing_successful())
        await self.server.unregister_modules()
        self.assertFalse(await is_executing_successful())

        await self.server.remove_modules(module)

    async def test_server_sc_server(self):
        async def terminate():
            await asyncio.sleep(0.01)
            asyncio.get_event_loop().stop()

        async with self.server.register_modules():
            asyncio.create_task(terminate())
            self.server.serve()
