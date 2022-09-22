"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import signal
from abc import ABC, abstractmethod
from typing import Callable

from sc_client import client

from sc_kpm.identifiers import _IdentifiersResolver
from sc_kpm.logging import get_kpm_logger
from sc_kpm.sc_module import ScModuleAbstract

_logger = get_kpm_logger()


class ScServerAbstract(ABC):
    """ScServer connects to server and stores"""

    @abstractmethod
    def connect(self) -> _Finisher:
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

    def register_modules(self) -> _Finisher:
        """Register all modules in the server"""

    def unregister_modules(self) -> None:
        """Unregister all modules from the server"""

    def start(self) -> _Finisher:
        """Connect and register modules"""

    def stop(self) -> None:
        """Disconnect and unregister modules"""


class ScServer(ScServerAbstract):
    def __init__(self, sc_server_url: str) -> None:
        self._url: str = sc_server_url
        self._modules: list[ScModuleAbstract] = []
        self.is_registered = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(repr, self._modules))})"

    def connect(self) -> _Finisher:
        client.connect(self._url)
        _logger.info("%s connected by url %s", self.__class__.__name__, repr(self._url))
        _IdentifiersResolver.resolve()
        return _Finisher(self.disconnect)

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

    def register_modules(self) -> _Finisher:
        if self.is_registered:
            _logger.warning("%s failed to register: modules are already registered", self.__class__.__name__)
        else:
            self._register(*self._modules)
            self.is_registered = True
            _logger.info("%s registered modules successfully", self.__class__.__name__)
        return _Finisher(self.unregister_modules)

    def unregister_modules(self) -> None:
        if not self.is_registered:
            _logger.warning("%s failed to unregister: modules are already unregistered", self.__class__.__name__)
            return
        self._unregister(*self._modules)
        self.is_registered = False
        _logger.info("%s unregistered modules successfully", self.__class__.__name__)

    def start(self) -> _Finisher:
        self.connect()
        self.register_modules()
        return _Finisher(self.stop)

    def stop(self) -> None:
        self.unregister_modules()
        self.disconnect()

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


class _Finisher:
    """Class for calling finish method in with-statement"""

    def __init__(self, finish_method: Callable[[], None]) -> None:
        self._finish_method = finish_method

    def __enter__(self) -> None:
        pass  # Interaction through the beginning method (with server.start_method(): ...)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            _logger.error("Raised error %s, ending", repr(exc_val))
        self._finish_method()
