"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import signal
from abc import ABC, abstractmethod

from sc_client import client

from sc_kpm.identifiers import _IdentifiersResolver
from sc_kpm.logging import get_kpm_logger
from sc_kpm.sc_module import ScModuleAbstract

_logger = get_kpm_logger()


class ScServerAbstract(ABC):
    """ScServer connects to server and stores"""

    @abstractmethod
    def connect(self) -> None:
        """Connect to server"""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the server"""

    @abstractmethod
    def add_modules(self, *modules: ScModuleAbstract) -> None:
        """Add modules to the server and register them if server is registered"""

    @abstractmethod
    def remove_modules(self, *modules: ScModuleAbstract) -> None:
        """Remove modules from the server and unregister them if server is registered"""

    def register_modules(self) -> _ScServerDisconnector:
        """Register all modules in the server"""

    def unregister_modules(self) -> None:
        """Unregister all modules from the server"""


class ScServer(ScServerAbstract):
    def __init__(self, sc_server_url: str) -> None:
        self._url: str = sc_server_url
        self._modules: list[ScModuleAbstract] = []
        self.is_registered = False

    def __enter__(self) -> None:
        pass  # Interaction through the register method (with server.register_modules(): ...)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.unregister_modules()

    def connect(self) -> _ScServerDisconnector:
        client.connect(self._url)
        _logger.info("%s connected by url %s", self.__class__.__name__, repr(self._url))
        _IdentifiersResolver.resolve()
        return _ScServerDisconnector(self)

    def disconnect(self) -> None:
        client.disconnect()
        _logger.info("%s disconnected", self.__class__.__name__)

    def add_modules(self, *modules: ScModuleAbstract) -> None:
        if self.is_registered:
            self._register(*modules)
        self._modules.extend(modules)
        _logger.info("%s added modules %s", self.__class__.__name__, ", ".join(map(repr, modules)))

    def remove_modules(self, *modules: ScModuleAbstract) -> None:
        if self.is_registered:
            self._unregister(*modules)
        _logger.info("%s removed modules %s", self.__class__.__name__, ", ".join(map(repr, modules)))

    def register_modules(self) -> ScServer:
        if self.is_registered:
            _logger.warning("%s failed to register: modules are already registered", self.__class__.__name__)
        else:
            self._register(*self._modules)
            self.is_registered = True
            _logger.info("%s registered modules successfully", self.__class__.__name__)
        return self

    def unregister_modules(self) -> None:
        if not self.is_registered:
            _logger.warning("%s failed to unregister: modules are already unregistered", self.__class__.__name__)
            return
        self._unregister(*self._modules)
        self.is_registered = False
        _logger.info("%s unregistered modules successfully", self.__class__.__name__)

    def _register(self, *modules: ScModuleAbstract) -> None:
        if not client.is_connected():
            _logger.error("%s failed to register: connection lost", self.__class__.__name__)
            raise ConnectionError("Connection lost")
        for module in modules:
            if not isinstance(module, ScModuleAbstract):
                _logger.error(
                    "%s failed to register: type of %s is not ScModule", self.__class__.__name__, repr(module)
                )
                raise TypeError("All elements of the module list must be ScModule instances")
            module._register()  # pylint: disable=protected-access

    def _unregister(self, *modules: ScModuleAbstract) -> None:
        if not client.is_connected():
            _logger.error("%s failed to unregister: connection lost", self.__class__.__name__)
            raise ConnectionError("Connection lost")
        for module in modules:
            module._unregister()  # pylint: disable=protected-access

    @staticmethod
    def wait_for_sigint() -> None:
        """Stop the program until a SIGINT signal (^C, or stop in IDE) is received"""

        signal.signal(signal.SIGINT, lambda *_: _logger.info("^C SIGINT was interrupted"))
        signal.pause()


class _ScServerDisconnector:
    """Class for calling server.disconnect() in with-statement"""

    def __init__(self, server: ScServer) -> None:
        self._server = server

    def __enter__(self) -> None:
        pass  # Interaction through the connect method (with server.connect(): ...)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            _logger.error("Raised error %s, unregistration agents", repr(exc_val))
        self._server.disconnect()
