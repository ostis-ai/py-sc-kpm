"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from sc_client import client

from sc_kpm.identifiers import _IdentifiersResolver
from sc_kpm.logging import get_kpm_logger
from sc_kpm.sc_module import ScModule

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
    def remove_modules(self, *modules: ScModule) -> None:
        """Remove modules"""

    @abstractmethod
    def add_modules(self, *modules: ScModule) -> None:
        """Add modules"""


class ScServer(ScServerAbstract):
    def __init__(self, sc_server_url: str):
        self._modules: list[ScModule] = []
        self._registrator = ScServerRegistrator(self._modules)
        self._url: str = sc_server_url

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        client.connect(self._url)
        _logger.info("%s connected by url %s", self.__class__.__name__, repr(self._url))
        _IdentifiersResolver.resolve()
        return self

    def disconnect(self):
        client.disconnect()
        _logger.info("%s disconnected", self.__class__.__name__)

    def add_modules(self, *modules: ScModule) -> None:
        self._modules.extend(modules)
        _logger.info("%s added modules %s", self.__class__.__name__, ", ".join(map(repr, modules)))
        if self._registrator.is_registered:
            self._registrator._register_modules(*modules)  # pylint: disable=protected-access

    def remove_modules(self, *modules: ScModule) -> None:
        if self._registrator.is_registered:
            self._registrator._unregister_modules(*modules)  # pylint: disable=protected-access
        _logger.info("%s removed modules %s", self.__class__.__name__, ", ".join(map(repr, modules)))

    def register_modules(self) -> ScServerRegistrator:
        self._registrator.register()
        return self._registrator

    def unregister_modules(self) -> None:
        self._registrator.unregister()


class ScServerRegistrator:
    """ScServerRegistrator registers and unregisters modules"""

    def __init__(self, modules: ScServer):
        self._modules = modules
        self.is_registered = False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            _logger.error("Raised error %s, unregistration agents", repr(exc_val))
        self.unregister()

    def register(self) -> None:
        if self.is_registered:
            _logger.warning("%s failed to register: modules are already registered", self.__class__.__name__)
            return
        self._register_modules(*self._modules)
        self.is_registered = True
        _logger.info("%s registered modules successfully", self.__class__.__name__)

    def unregister(self) -> None:
        if not self.is_registered:
            _logger.warning("%s failed to unregister: modules are already unregistered", self.__class__.__name__)
            return
        self._unregister_modules(*self._modules)
        self.is_registered = False
        _logger.info("%s unregistered modules successfully", self.__class__.__name__)

    def _register_modules(self, *modules: ScModule) -> None:
        if not client.is_connected():
            _logger.error("%s failed to register: connection lost", self.__class__.__name__)
            raise ConnectionError("Connection lost")
        for module in modules:
            if not isinstance(module, ScModule):
                _logger.error(
                    "%s failed to register: type error: %s is not module", self.__class__.__name__, repr(module)
                )
                raise TypeError("All elements of the module list must be ScModule instances")
            module._try_register()  # pylint: disable=protected-access

    def _unregister_modules(self, *modules: ScModule) -> None:
        if not client.is_connected():
            # TODO: How to unregister agents without connection?
            _logger.error(
                "%s failed to unregister: connection lost, events left in the system", self.__class__.__name__
            )
            raise ConnectionError("Connection lost")
        for module in modules:
            module._unregister()  # pylint: disable=protected-access
