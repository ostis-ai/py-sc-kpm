"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import os
import signal
import threading

from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr

from sc_kpm import ScAgent, ScAgentClassic, ScModule, ScResult
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.utils.action_utils import execute_agent, finish_action_with_status
from tests.common_tests import BaseTestCase

WAIT_TIME = 1


class CommonTests(BaseTestCase):
    def test_sc_agents(self):
        class Agent(ScAgent):
            ACTION_CLASS_NAME = "test_agent"

            def __init__(self):
                super().__init__(self.ACTION_CLASS_NAME, ScEventType.ADD_OUTGOING_EDGE)

            def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                finish_action_with_status(action_element, True)
                return ScResult.OK

        class AgentClassic(ScAgentClassic):
            ACTION_CLASS_NAME = "test_agent_classic"

            def __init__(self):
                super().__init__(self.ACTION_CLASS_NAME)

            def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                finish_action_with_status(action_element, True)
                return ScResult.OK

        module = ScModule(Agent(), AgentClassic())
        self.server.add_modules(module)
        kwargs = dict(
            arguments={},
            concepts=[],
            initiation=Agent.ACTION_CLASS_NAME,
            wait_time=WAIT_TIME,
        )
        kwargs_classic = dict(
            arguments={},
            concepts=[CommonIdentifiers.ACTION, AgentClassic.ACTION_CLASS_NAME],
            wait_time=WAIT_TIME,
        )
        self.assertFalse(execute_agent(**kwargs)[1])
        self.assertFalse(execute_agent(**kwargs_classic)[1])
        with self.server.register_modules():
            self.assertTrue(execute_agent(**kwargs)[1])
            self.assertTrue(execute_agent(**kwargs_classic)[1])
        self.assertFalse(execute_agent(**kwargs)[1])
        self.assertFalse(execute_agent(**kwargs_classic)[1])
        self.server.remove_modules(module)

    def test_sc_module(self):
        class TestAgent(ScAgent):
            def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
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
        self.server.add_modules(module1)
        module1.add_agent(agent3)
        with self.server.register_modules():
            self.assertTrue(is_executing_successful(1))
            self.assertFalse(is_executing_successful(2))
            self.assertTrue(is_executing_successful(3))

            self.server.add_modules(module2)
            self.assertTrue(is_executing_successful(2))

            module1.remove_agent(agent3)
            self.assertTrue(is_executing_successful(1))
            self.assertFalse(is_executing_successful(3))
            self.server.remove_modules(module1, module2)

    def test_sc_server(self):
        class TestAgent(ScAgent):
            ACTION_CLASS_NAME = "some_agent"

            def __init__(self):
                super().__init__(self.ACTION_CLASS_NAME, ScEventType.ADD_OUTGOING_EDGE)

            def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
                finish_action_with_status(action_element, True)
                return ScResult.OK

        def is_executing_successful() -> bool:
            return execute_agent(
                arguments={},
                concepts=[],
                initiation=TestAgent.ACTION_CLASS_NAME,
                wait_time=WAIT_TIME,
            )[1]

        module = ScModule(TestAgent())
        self.server.add_modules(module)
        self.assertFalse(is_executing_successful())
        self.server.register_modules()
        self.assertTrue(is_executing_successful())
        self.server.unregister_modules()
        self.assertFalse(is_executing_successful())

        main_pid = os.getpid()

        def execute_and_send_sigint():
            self.assertTrue(is_executing_successful())
            os.kill(main_pid, signal.SIGINT)
            self.assertFalse(is_executing_successful())

        with self.server.register_modules():
            thread = threading.Thread(target=execute_and_send_sigint, daemon=True)
            thread.start()
            self.server.serve()

        self.server.remove_modules(module)
