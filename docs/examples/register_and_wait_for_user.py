"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""

import logging

from sc_kpm import ScAddr, ScAgentClassic, ScModule, ScResult, ScServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestScAgent(ScAgentClassic):
    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        logger.info("Agent's called")
        if not self._confirm_action_class(action_element):
            return ScResult.SKIP
        logger.info("Agent's confirmed and started")
        return ScResult.OK


SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)
with server.connect():
    module = ScModule(TestScAgent("sum_action_class"))
    server.add_modules(module)
    with server.register_modules():
        server.wait_for_sigint()
