"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""
import logging

from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType

from sc_kpm import ScAgent, ScKeynodes, ScModule, ScServer
from sc_kpm.common import CommonIdentifiers, QuestionStatus
from sc_kpm.common.sc_result import ScResult
from sc_kpm.utils.action_utils import check_action_class, execute_agent
from sc_kpm.utils.common_utils import create_edge, create_node, delete_elements

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
test_node_idtf = "test_node"

SC_SERVER_URL = "ws://localhost:8090/ws_json"


class ScAgentTest(ScAgent):
    def on_event(self, _src, _edge, target_node) -> ScResult:
        logger.info(f"{self.__class__.__name__} is started")
        for status in (QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY, QuestionStatus.QUESTION_FINISHED):
            create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, ScKeynodes()[status.value], target_node)
        return ScResult.OK


class ScModuleTest(ScModule):
    def __init__(self):
        self.add_agent(ScAgentTest, test_node_idtf, ScEventType.ADD_OUTGOING_EDGE)
        self.add_agent(ScAgentTest, test_node_idtf, ScEventType.ADD_INGOING_EDGE)


def call_agent(sc_server):
    module = ScModuleTest()
    sc_server.add_modules(module)
    node = create_node(sc_types.NODE_CONST, test_node_idtf)
    node.is_valid()
    reaction = QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY
    execute_agent({}, [], test_node_idtf, reaction=reaction)
    sc_server.remove_modules(module)


if __name__ == "__main__":
    server = ScServer(SC_SERVER_URL)
    server.start()
    call_agent(server)
    server.stop()
