"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging

from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType

from sc_kpm import ScAgent, ScKeynodes, ScModule
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.sc_result import ScResult
from sc_kpm.utils.action_utils import check_action_class, execute_agent, finish_action_with_status
from sc_kpm.utils.common_utils import create_edge, create_node, delete_elements
from tests.common_tests import BaseTestCase

logging.basicConfig(filename="testing.log", filemode="w", level=logging.DEBUG)
logger = logging.getLogger(__name__)
test_node_idtf = "test_node"


class ScAgentTest(ScAgent):
    def on_event(self, _src, _edge, target_node) -> ScResult:
        logger.info(f"{self.__class__.__name__} is started")
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
        action_class = "test_action_class"
        question = ScKeynodes()[CommonIdentifiers.QUESTION]
        test_node = create_node(sc_types.NODE_CONST)
        action_class_node = create_node(sc_types.NODE_CONST, action_class)
        assert check_action_class(action_class_node, test_node) is False
        assert check_action_class(action_class, test_node) is False
        class_edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, action_class_node, test_node)
        assert check_action_class(action_class_node, test_node) is False
        assert check_action_class(action_class, test_node) is False
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, question, test_node)
        assert check_action_class(action_class_node, test_node)
        assert check_action_class(action_class, test_node)
        delete_elements(class_edge)
        assert check_action_class(action_class_node, test_node) is False
        assert check_action_class(action_class, test_node) is False

    def test_call_agent(self):
        module = ScModuleTest()
        self.server.add_modules(module)
        with self.server.register_modules():
            assert execute_agent({}, [], test_node_idtf)[1]
        self.server.remove_modules(module)
