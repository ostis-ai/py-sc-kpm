"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import logging
from unittest import IsolatedAsyncioTestCase

from asc_kpm.asc_server import AScServer

SC_SERVER_URL = "ws://localhost:8090/ws_json"

logging.basicConfig(filename="../testing.log", filemode="w", level=logging.INFO, force=True)


class AsyncioScKpmTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.logger = logging.getLogger(f"{self.__module__}.{self.__class__.__name__}")
        self.server = AScServer(SC_SERVER_URL)
        await self.server.connect()

    async def asyncTearDown(self) -> None:
        await self.server.disconnect()
