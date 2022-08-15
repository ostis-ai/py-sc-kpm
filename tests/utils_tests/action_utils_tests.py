"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types

from sc_common.identifiers import CommonIdentifiers, QuestionStatus
from sc_common.sc_keynodes import ScKeynodes
from sc_utils.action_utils import validate_action, call_agent
from sc_utils.common_utils import generate_node, generate_edge, delete_edge, delete_elements
from tests.common_tests import BaseTestCase, TestAgent


class TestActionUtils(BaseTestCase):
    def test_validate_action(self):
        action_class = "test_action_class"
        question = ScKeynodes()[CommonIdentifiers.QUESTION.value]
        test_node = generate_node(sc_types.NODE_CONST)
        action_class_node = generate_node(sc_types.NODE_CONST, action_class)
        self.assertFalse(validate_action(action_class_node, test_node))
        self.assertFalse(validate_action(action_class, test_node))
        class_edge = generate_edge(action_class_node, sc_types.EDGE_ACCESS_CONST_POS_PERM, test_node)
        self.assertFalse(validate_action(action_class_node, test_node))
        self.assertFalse(validate_action(action_class, test_node))
        generate_edge(question, sc_types.EDGE_ACCESS_CONST_POS_PERM, test_node)
        self.assertTrue(validate_action(action_class_node, test_node))
        self.assertTrue(validate_action(action_class, test_node))
        delete_elements(class_edge)
        self.assertFalse(validate_action(action_class_node, test_node))
        self.assertFalse(validate_action(action_class, test_node))

    def test_call_agent(self):
        agent = TestAgent()
        node = generate_node(sc_types.NODE_CONST, agent.source_node)
        self.assertTrue(node.is_valid())
        agent.register()
        self.assertTrue(
            call_agent({}, [], agent.source_node, reaction=QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY)
        )


