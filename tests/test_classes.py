"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_kpm import ScAddr, ScAgent, ScAgentClassic, ScEventType, ScModule, ScResult
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.utils.action_utils import execute_agent, finish_action_with_status
from tests.common_tests import BaseTestCase, server

WAIT_TIME = 1


class CommonTests(BaseTestCase):
    def test_sc_agents(self):
        class Agent(ScAgent):
            ACTION_CLASS_NAME = "Stalin_3000"

            def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
                finish_action_with_status(action_element, True)
                return ScResult.OK

        class AgentClassic(ScAgentClassic):
            def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
                if not self._confirm_action_class(action_element):
                    return ScResult.SKIP
                finish_action_with_status(action_element, True)
                return ScResult.OK

        agent = Agent(event_class=Agent.ACTION_CLASS_NAME, event_type=ScEventType.ADD_OUTGOING_EDGE)
        agent_classic = AgentClassic(classic_class_name := "classic")
        server.add_modules(ScModule(agent, agent_classic))
        kwargs = dict(
            arguments={},
            concepts=[],
            initiation=Agent.ACTION_CLASS_NAME,
            wait_time=WAIT_TIME,
        )
        kwargs_classic = dict(
            arguments={},
            concepts=[CommonIdentifiers.QUESTION.value, classic_class_name],
            wait_time=WAIT_TIME,
        )
        self.assertFalse(execute_agent(**kwargs)[1])
        self.assertFalse(execute_agent(**kwargs_classic)[1])
        with server.register_modules():
            self.assertTrue(execute_agent(**kwargs)[1])
            self.assertTrue(execute_agent(**kwargs_classic)[1])
        self.assertFalse(execute_agent(**kwargs)[1])
        self.assertFalse(execute_agent(**kwargs_classic)[1])

    def test_sc_module(self):
        class TestAgent(ScAgent):
            def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
                finish_action_with_status(action_element, True)
                return ScResult.OK

        def is_executing_successful(i: int) -> bool:
            return execute_agent(
                arguments={},
                concepts=[],
                initiation=f"agent{i}",
                wait_time=WAIT_TIME,
            )[1]

        agent1 = TestAgent("agent1", ScEventType.ADD_OUTGOING_EDGE)
        agent2 = TestAgent("agent2", ScEventType.ADD_OUTGOING_EDGE)
        agent3 = TestAgent("agent3", ScEventType.ADD_OUTGOING_EDGE)

        module1 = ScModule(agent1)
        module2 = ScModule(agent2)
        server.add_modules(module1)
        module1.add_agent(agent3)
        with server.register_modules():
            module1.add_agent(agent2)  # Cannot add agent to module in register time
            self.assertTrue(is_executing_successful(1))
            self.assertFalse(is_executing_successful(2))
            self.assertTrue(is_executing_successful(3))

            server.add_modules(module2)
            self.assertTrue(is_executing_successful(2))

            server.remove_modules(module1)
            module1.remove_agent(agent3)
            server.add_modules(module1)
            self.assertTrue(is_executing_successful(1))
            self.assertFalse(is_executing_successful(3))

    def test_sc_server(self):
        class TestAgent(ScAgent):
            def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
                finish_action_with_status(action_element, True)
                return ScResult.OK

        name = "some_agent"

        def is_executing_successful() -> bool:
            return execute_agent(
                arguments={},
                concepts=[],
                initiation=name,
                wait_time=WAIT_TIME,
            )[1]

        module = ScModule(TestAgent(name, ScEventType.ADD_OUTGOING_EDGE))
        server.add_modules(module)
        self.assertFalse(is_executing_successful())
        with server.register_modules():
            self.assertTrue(is_executing_successful())
        self.assertFalse(is_executing_successful())

        server.register_modules()
        self.assertTrue(is_executing_successful())
        server.remove_modules(module)
        self.assertFalse(is_executing_successful())
        server.add_modules(module)
        server.unregister_modules()
        self.assertFalse(is_executing_successful())
