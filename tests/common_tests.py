"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from unittest import TestCase

import sc_client.client


SC_SERVER_URL = "ws://localhost:8090/ws_json"


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        sc_client.client.connect(SC_SERVER_URL)

    def tearDown(self) -> None:
        sc_client.client.disconnect()
