"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from sc_client import client

from sc_kpm.identifiers import _IdentifiersResolver
from sc_kpm.sc_module import ScModule


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
    def __init__(self, default_sc_server_url: str):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._modules: list[ScModule] = []
        self._registrator = ScServerRegistrator(self._modules)
        self._url: str = default_sc_server_url

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        client.connect(self._url)
        self._logger.info("Connect to server by url %s", repr(self._url))
        _IdentifiersResolver.resolve()
        return self

    def disconnect(self):
        client.disconnect()
        self._logger.info("Disconnect from the server")

    def add_modules(self, *modules: ScModule) -> None:
        self._modules.extend(modules)
        self._logger.info("Add modules %s", repr(modules))
        if self._registrator.is_registered:
            self._registrator._register_modules(*modules)  # pylint: disable=protected-access

    def remove_modules(self, *modules: ScModule) -> None:
        if self._registrator.is_registered:
            self._registrator._unregister_modules(*modules)  # pylint: disable=protected-access
        self._logger.info("Remove modules %s", repr(modules))

    def register_modules(self) -> ScServerRegistrator:
        self._registrator.register()
        return self._registrator

    def unregister_modules(self) -> None:
        self._registrator.unregister()


class ScServerRegistrator:
    """ScServerRegistrator registers and unregisters modules"""

    def __init__(self, modules: ScServer):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._modules = modules
        self.is_registered = False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self._logger.error("Raised error %s, unregistration agents", repr(exc_val))
        self.unregister()

    def register(self) -> None:
        if self.is_registered:
            self._logger.warning("Modules are already registered")
            return
        self._register_modules(*self._modules)
        self.is_registered = True

    def unregister(self) -> None:
        if not self.is_registered:
            self._logger.warning("Modules are already unregistered")
            return
        self._unregister_modules(*self._modules)
        self.is_registered = False

    @staticmethod
    def _register_modules(*modules: ScModule):
        if not client.is_connected():
            raise ConnectionError("Connection to the sc-server is not established")
        for module in modules:
            if not isinstance(module, ScModule):
                raise TypeError("All elements of the module list must be ScModule instances")
            module._try_register()  # pylint: disable=protected-access

    @staticmethod
    def _unregister_modules(*modules: ScModule):
        if not client.is_connected():
            # TODO: How to unregister agents without connection?
            raise ConnectionError("Connection to the sc-server is not established")
        for module in modules:
            module._unregister()  # pylint: disable=protected-access
