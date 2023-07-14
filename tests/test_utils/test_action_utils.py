"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.client import delete_elements
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType

from sc_kpm import ScAgent, ScKeynodes, ScModule
from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus
from sc_kpm.sc_result import ScResult
from sc_kpm.utils.action_utils import (
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
from sc_kpm.utils.common_utils import check_edge, create_edge, create_node
from tests.common_tests import BaseTestCase

test_node_idtf = "test_node"


class ScAgentTest(ScAgent):
    def on_event(self, _src, _edge, target_node) -> ScResult:
        self.logger.info(f"Agent's started")
        finish_action_with_status(target_node)
        return ScResult.OK


class ScModuleTest(ScModule):
    def __init__(self):
        super().__init__(
            ScAgentTest(test_node_idtf, ScEventType.ADD_OUTGOING_EDGE),
            ScAgentTest(test_node_idtf, ScEventType.ADD_INGOING_EDGE),
        )


class TestActionUtils(BaseTestCase):
    def test_validate_action(self):
        action_class_idtf = "test_action_class"
        action_class_node = ScKeynodes.resolve(action_class_idtf, sc_types.NODE_CONST)
        question = ScKeynodes[CommonIdentifiers.QUESTION]
        test_node = create_node(sc_types.NODE_CONST)
        self.assertFalse(check_action_class(action_class_node, test_node))
        self.assertFalse(check_action_class(action_class_idtf, test_node))
        class_edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, action_class_node, test_node)
        self.assertFalse(check_action_class(action_class_node, test_node))
        self.assertFalse(check_action_class(action_class_idtf, test_node))
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, question, test_node)
        self.assertTrue(check_action_class(action_class_node, test_node))
        self.assertTrue(check_action_class(action_class_idtf, test_node))
        delete_elements(class_edge)
        self.assertFalse(check_action_class(action_class_node, test_node))
        self.assertFalse(check_action_class(action_class_idtf, test_node))

    def test_execute_agent(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            assert execute_agent({}, [], test_node_idtf)[1]
        self.server.remove_modules(module)

    def test_call_agent(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            question = call_agent({}, [], test_node_idtf)
            wait_agent(1, question, ScKeynodes[QuestionStatus.QUESTION_FINISHED])
            result = check_edge(
                sc_types.EDGE_ACCESS_VAR_POS_PERM, ScKeynodes[QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY], question
            )
            self.assertTrue(result)
        self.server.remove_modules(module)

    def test_wrong_execute_agent(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            self.assertFalse(execute_agent({}, [], "wrong_agent", wait_time=1)[1])
        self.server.remove_modules(module)

    def test_execute_action(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            action_node = create_action()
            add_action_arguments(action_node, {})
            assert execute_action(action_node, test_node_idtf)
        self.server.remove_modules(module)

    def test_call_action(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            action_node = create_action()
            add_action_arguments(action_node, {})
            call_action(action_node, test_node_idtf)
            wait_agent(1, action_node, ScKeynodes[QuestionStatus.QUESTION_FINISHED])
            result = check_edge(
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes[QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY],
                action_node,
            )
            self.assertTrue(result)
        self.server.remove_modules(module)

    def test_wrong_execute_action(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            action_node = create_action()
            add_action_arguments(action_node, {})
            self.assertFalse(execute_action(action_node, "wrong_agent", wait_time=1))
        self.server.remove_modules(module)
