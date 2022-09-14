"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""

import logging
import signal

from sc_kpm import ScAddr, ScAgentClassic, ScModule, ScResult, ScServer


class TestScAgent(ScAgentClassic):
    def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_node: ScAddr) -> ScResult:
        self._logger.info("Agent's called")
        if not self._confirm_action_class(action_node):
            return ScResult.SKIP
        self._logger.info("Agent's confirmed and started")
        return ScResult.OK


logging.basicConfig(level=logging.INFO)
SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)
with server.connect():
    module = ScModule(TestScAgent("sum_action_class"))
    server.add_modules(module)
    with server.register_modules():
        signal.signal(signal.SIGINT, lambda *_: logging.getLogger(__file__).info("^C interrupted"))
        signal.pause()  # Waiting for ^C
