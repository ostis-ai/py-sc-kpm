"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import asyncio
from logging import Logger, getLogger
from typing import Awaitable, Callable

from sc_client.core.asc_client_instance import asc_client

from asc_kpm.asc_keynodes_ import asc_keynodes
from asc_kpm.asc_module import AScModule
from sc_kpm.identifiers import _IdentifiersResolver


class AScServer:
    """ScServer connects to the server and stores modules"""

    def __init__(self, sc_server_url: str) -> None:
        self._url: str = sc_server_url
        self._modules: set[AScModule] = set()
        self.is_registered = False
        self.logger = getLogger(f"{self.__module__}.{self.__class__.__name__}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(repr, self._modules))})"

    def connect(self) -> _AFinisher:
        """Connect to server"""

        async def enter():
            await asc_client.connect(self._url)
            self.logger.info("Connected by url: %s", repr(self._url))
            asc_client.set_on_reconnect_handler(self._register_after_reconnect)
            await self.resolve_identifiers()

        return _AFinisher(enter, self.disconnect, self.logger)

    @staticmethod
    async def resolve_identifiers():
        types_map = _IdentifiersResolver.get_types_map()
        if types_map is None:
            return
        for idtf, sc_type in types_map:
            await asc_keynodes.resolve(idtf, sc_type)

    async def disconnect(self) -> None:
        """Disconnect from the server"""
        await asc_client.disconnect()
        self.logger.info("Disconnected from url: %s", repr(self._url))

    async def add_modules(self, *modules: AScModule) -> None:
        """Add modules to the server and register them if server is registered"""
        if self.is_registered:
            await self._register(*modules)
        self._modules |= {*modules}
        self.logger.info("Added modules: %s", ", ".join(map(repr, modules)))

    async def remove_modules(self, *modules: AScModule) -> None:
        """Remove modules from the server and unregister them if server is registered"""
        if self.is_registered:
            await self._unregister(*modules)
        self._modules -= {*modules}
        self.logger.info("Removed modules: %s", ", ".join(map(repr, modules)))

    async def clear_modules(self) -> None:
        """Remove all modules from the server and unregister them if server is registered"""
        if self.is_registered:
            await self._unregister(*self._modules)
        self.logger.info("Removed all modules: %s", ", ".join(map(repr, self._modules)))
        self._modules.clear()

    def register_modules(self) -> _AFinisher:
        """Register all modules in the server"""

        async def enter():
            if self.is_registered:
                self.logger.warning("Modules are already registered")
            else:
                await self._register(*self._modules)
                self.is_registered = True
                self.logger.info("Registered modules successfully")

        return _AFinisher(enter, self.unregister_modules, self.logger)

    async def unregister_modules(self) -> None:
        """Unregister all modules from the server"""
        if not self.is_registered:
            self.logger.warning("Modules are already unregistered")
            return
        await self._unregister(*self._modules)
        self.is_registered = False
        self.logger.info("Unregistered modules successfully")

    async def _register_after_reconnect(self):
        if not self.is_registered:
            return
        await self._unregister(*self._modules)
        await self._register(*self._modules)
        self.logger.info("Re-registered modules successfully")

    def start(self) -> _AFinisher:
        """Connect and register modules"""

        async def enter():
            await self.connect()
            await self.register_modules()

        return _AFinisher(enter, self.stop, self.logger)

    async def stop(self) -> None:
        """Disconnect and unregister modules"""
        await self.unregister_modules()
        await self.disconnect()

    async def _register(self, *modules: AScModule) -> None:
        if not asc_client.is_connected():
            self.logger.error("Failed to register: connection lost")
            raise ConnectionError(f"Connection to url {repr(self._url)} lost")
        for module in modules:
            if not isinstance(module, AScModule):
                self.logger.error("Failed to register: type of %s is not ScModule", repr(module))
                raise TypeError(f"{repr(module)} is not ScModule")
            await module._register()  # pylint: disable=protected-access

    async def _unregister(self, *modules: AScModule) -> None:
        if not asc_client.is_connected():
            self.logger.error("Failed to unregister: connection to %s lost", repr(self._url))
            raise ConnectionError(f"Connection to {repr(self._url)} lost")
        for module in modules:
            await module._unregister()  # pylint: disable=protected-access

    def serve(self) -> None:
        """Serve agents until a SIGINT signal (^C, or stop in IDE) is received"""
        self.logger.info("* Serving ScServer...")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.logger.info("^C SIGINT was interrupted")


class _AFinisher:
    """Class for calling finish method in with-statement"""

    def __init__(
        self, enter_method: Callable[[], Awaitable], exit_method: Callable[[], Awaitable], logger: Logger
    ) -> None:
        self._enter_method = enter_method
        self._exit_method = exit_method
        self._logger = logger

    def __await__(self):
        return self._enter_method().__await__()

    async def __aenter__(self) -> None:
        await self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            self._logger.error("Raised error %s, finishing", repr(exc_val))
        await self._exit_method()
