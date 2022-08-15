"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
from unittest import TestCase

import sc_client.client
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType

from sc_common.identifiers import QuestionStatus
from sc_common.sc_agent import ScAgent
from sc_common.sc_keynodes import ScKeynodes
from sc_common.sc_module import ScModule, register_sc_modules, unregister_sc_modules
from sc_utils.common_utils import generate_node, generate_edge


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        sc_client.client.connect("ws://localhost:8090/ws_json")

    def tearDown(self) -> None:
        sc_client.client.disconnect()


test_node_1 = "test_idtf_1"
test_node_2 = "test_idtf_2"
test_node_x = "test_idtf_x"


class TestAgent(ScAgent):
    @classmethod
    def setup(cls):
        cls.source_node = test_node_1
        cls.event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(source_node, edge, target_node):
        print(f"{TestAgent.__name__} is started")
        for status in (QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY, QuestionStatus.QUESTION_FINISHED):
            status = ScKeynodes()[status.value]
            generate_edge(status, sc_types.EDGE_ACCESS_CONST_POS_PERM, target_node)


class TestAgent2(ScAgent):
    @classmethod
    def setup(cls):
        cls.source_node = test_node_2
        cls.event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(source_node, edge, target_node):
        print(f"{TestAgent2.__name__} agent  agent called!!!!!!!!!!!!!!!!!!!!!!!!!")


class TestAgentX(ScAgent):
    @classmethod
    def setup(cls):
        cls.source_node = test_node_x
        cls.event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(source_node, edge, target_node):
        print(f"{TestAgentX.__name__} agent called!!!!!!!!!!!!!!!!!!!!!!!!!")


class TestScModuleSingleAgent(ScModule):
    agents = [TestAgent()]


class TestScModuleMultipleAgent(ScModule):
    agents = [TestAgent2(), TestAgentX()]


class TestScModuleEmptyAgent(ScModule):
    agents = []


# sc_client.client.connect("ws://localhost:8090/ws_json")
#
# for idtf in (test_node_1, test_node_2, test_node_x):
#     generate_node(sc_types.NODE_CONST_CLASS, idtf)
#
# TestScModuleSingleAgent()
# TestScModuleMultipleAgent()
# TestScModuleEmptyAgent()
# register_sc_modules()
#
# node1 = ScKeynodes()[test_node_1]
# node2 = generate_node(sc_types.NODE_CONST)
# generate_edge(node1, node2, sc_types.EDGE_ACCESS_CONST_POS_PERM)
#
# unregister_sc_modules()
# sc_client.client.disconnect()
