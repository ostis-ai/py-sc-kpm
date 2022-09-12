"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from unittest import TestCase

from sc_kpm import ScServer

SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        server.connect()

    def tearDown(self) -> None:
        server.disconnect()
