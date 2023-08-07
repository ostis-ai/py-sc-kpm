"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""

import logging

from sc_client import ScAddr
from sc_kpm import ScAgentClassic, ScModule, ScResult, ScServer

logging.basicConfig(level=logging.INFO)


class TestScAgent(ScAgentClassic):
    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        return ScResult.OK


SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)
with server.connect():
    module = ScModule(TestScAgent("sum_action_class"))
    server.add_modules(module)
    with server.register_modules():
        server.serve()
