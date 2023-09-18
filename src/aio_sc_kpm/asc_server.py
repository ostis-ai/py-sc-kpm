"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import signal
from logging import Logger, getLogger
from typing import Awaitable, Callable

from aio_sc_kpm.client_ import client
from sc_kpm.identifiers import _IdentifiersResolver
from sc_kpm.sc_module import ScModuleAbstract


class AScServer:
    """ScServer connects to the server and stores modules"""

    def __init__(self, sc_server_url: str) -> None:
        self._url: str = sc_server_url
        self._modules: set[ScModuleAbstract] = set()
        self.is_registered = False
        self.logger = getLogger(f"{self.__module__}.{self.__class__.__name__}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(repr, self._modules))})"

    async def connect(self) -> _Finisher:
        """Connect to server"""
        await client.connect(self._url)
        self.logger.info("Connected by url: %s", repr(self._url))
        _IdentifiersResolver.resolve()
        return _Finisher(self.disconnect, self.logger)

    async def disconnect(self) -> None:
        """Disconnect from the server"""
        await client.disconnect()
        self.logger.info("Disconnected from url: %s", repr(self._url))

    async def add_modules(self, *modules: ScModuleAbstract) -> None:
        """Add modules to the server and register them if server is registered"""
        if self.is_registered:
            await self._register(*modules)
        self._modules |= {*modules}
        self.logger.info("Added modules: %s", ", ".join(map(repr, modules)))

    async def remove_modules(self, *modules: ScModuleAbstract) -> None:
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

    async def register_modules(self) -> _Finisher:
        """Register all modules in the server"""
        if self.is_registered:
            self.logger.warning("Modules are already registered")
        else:
            await self._register(*self._modules)
            self.is_registered = True
            self.logger.info("Registered modules successfully")
        return _Finisher(self.unregister_modules, self.logger)

    async def unregister_modules(self) -> None:
        """Unregister all modules from the server"""
        if not self.is_registered:
            self.logger.warning("Modules are already unregistered")
            return
        await self._unregister(*self._modules)
        self.is_registered = False
        self.logger.info("Unregistered modules successfully")

    async def start(self) -> _Finisher:
        """Connect and register modules"""
        await self.connect()
        await self.register_modules()
        return _Finisher(self.stop, self.logger)

    async def stop(self) -> None:
        """Disconnect and unregister modules"""
        await self.unregister_modules()
        await self.disconnect()

    async def _register(self, *modules: ScModuleAbstract) -> None:
        if not client.is_connected():
            self.logger.error("Failed to register: connection lost")
            raise ConnectionError(f"Connection to url {repr(self._url)} lost")
        for module in modules:
            if not isinstance(module, ScModuleAbstract):
                self.logger.error("Failed to register: type of %s is not ScModule", repr(module))
                raise TypeError(f"{repr(module)} is not ScModule")
            module._register()  # pylint: disable=protected-access

    async def _unregister(self, *modules: ScModuleAbstract) -> None:
        if not client.is_connected():
            self.logger.error("Failed to unregister: connection to %s lost", repr(self._url))
            raise ConnectionError(f"Connection to {repr(self._url)} lost")
        for module in modules:
            module._unregister()  # pylint: disable=protected-access

    def serve(self) -> None:
        """Serve agents until a SIGINT signal (^C, or stop in IDE) is received"""
        signal.signal(signal.SIGINT, lambda *_: self.logger.info("^C SIGINT was interrupted"))
        signal.pause()


class _Finisher:
    """Class for calling finish method in with-statement"""

    def __init__(self, finish_method: Callable[[], Awaitable], logger: Logger) -> None:
        self._finish_method = finish_method
        self._logger = logger

    async def __aenter__(self) -> None:
        pass  # Interaction through the beginning method (with server.start_method(): ...)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            self._logger.error("Raised error %s, finishing", repr(exc_val))
        await self._finish_method()
