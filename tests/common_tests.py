import sc_client.client
from sc_client.constants.common import ScEventType

from sc_common.sc_agent import ScAgent
from sc_common.sc_module import ScModule, register_sc_modules, unregister_sc_modules


class TestAgent1(ScAgent):
    source_node_idtf = "test_idtf_1"
    event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(source_node, edge, target_node):
        print(f"{TestAgent1.source_node_idtf} agent called")


class TestAgent2(ScAgent):
    source_node_idtf = "test_idtf_2"
    event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(source_node, edge, target_node):
        print(f"{TestAgent1.source_node_idtf} agent called")


class TestAgentX(ScAgent):
    source_node_idtf = "test_idtf_x"
    event_type = ScEventType.ADD_OUTGOING_EDGE

    @staticmethod
    def on_event(source_node, edge, target_node):
        print(f"{TestAgent1.source_node_idtf} agent called")


class TestScModuleSingleAgent(ScModule):
    agents = [TestAgent1()]


class TestScModuleMultipleAgent(ScModule):
    agents = [TestAgent2(), TestAgentX()]


class TestScModuleEmptyAgent(ScModule):
    agents = []


sc_client.client.connect("ws://localhost:8090/ws_json")
TestScModuleSingleAgent()
TestScModuleMultipleAgent()
TestScModuleEmptyAgent()
register_sc_modules()
unregister_sc_modules()
sc_client.client.disconnect()
