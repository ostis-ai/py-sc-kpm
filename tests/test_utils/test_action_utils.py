"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType

from sc_kpm import ScKeynodes, ScAgent
from sc_kpm.common import CommonIdentifiers, QuestionStatus
from sc_kpm.utils.action_utils import call_agent, validate_action
from sc_kpm.utils.common_utils import delete_elements, generate_edge, generate_node
from tests.common_tests import BaseTestCase
import logging

logging.basicConfig(filename="testing.log", filemode='w', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ExampleAgent(ScAgent):
    @classmethod
    def setup(cls):
        cls.source_node = "test_node"
        cls.event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(*_, target_node):
        logger.info(f"{ExampleAgent.__name__} is started")
        for status in (QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY, QuestionStatus.QUESTION_FINISHED):
            generate_edge(ScKeynodes()[status.value], sc_types.EDGE_ACCESS_CONST_POS_PERM, target_node)


class TestActionUtils(BaseTestCase):
    def test_validate_action(self):
        action_class = "test_action_class"
        question = ScKeynodes()[CommonIdentifiers.QUESTION.value]
        test_node = generate_node(sc_types.NODE_CONST)
        action_class_node = generate_node(sc_types.NODE_CONST, action_class)
        assert validate_action(action_class_node, test_node) is False
        assert validate_action(action_class, test_node) is False
        class_edge = generate_edge(action_class_node, sc_types.EDGE_ACCESS_CONST_POS_PERM, test_node)
        assert validate_action(action_class_node, test_node) is False
        assert validate_action(action_class, test_node) is False
        generate_edge(question, sc_types.EDGE_ACCESS_CONST_POS_PERM, test_node)
        assert validate_action(action_class_node, test_node)
        assert validate_action(action_class, test_node)
        delete_elements(class_edge)
        assert validate_action(action_class_node, test_node) is False
        assert validate_action(action_class, test_node) is False

    def test_call_agent(self):
        agent = ExampleAgent()
        node = generate_node(sc_types.NODE_CONST, agent.source_node)
        assert node.is_valid()
        agent.register()
        assert call_agent({}, [], agent.source_node, reaction=QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY)
