"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from sc_client import client

from sc_kpm.sc_module import ScModule


class ScServerAbstract(ABC):
    """ScServer connects to server and stores"""

    @abstractmethod
    def connect(self, sc_server_url: str) -> None:
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
    def __init__(self, default_sc_server_url: str = None):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._modules: list[ScModule] = []
        self._register = ScServerRegistrator(self._modules)
        self._default_url = default_sc_server_url

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self, sc_server_url: str = None):
        if sc_server_url is None:
            if self._default_url is None:
                raise ConnectionError("Connection failed: ScServer URL is None")
            sc_server_url = self._default_url
        client.connect(sc_server_url)
        self._logger.info("Connect to server by url %s", repr(sc_server_url))
        return self

    def disconnect(self):
        client.disconnect()
        self._logger.info("Disconnect from the server")

    def add_modules(self, *modules: ScModule) -> None:
        self._modules.extend(modules)
        self._logger.info("Add modules %s", repr(modules))
        if self._register.is_registered:
            self._register.register_modules(*modules)

    def remove_modules(self, *modules: ScModule) -> None:
        if self._register.is_registered:
            self._register.unregister_modules(*modules)
        self._logger.info("Remove modules %s", repr(modules))

    def register_modules(self) -> ScServerRegistrator:
        return self._register


class ScServerRegistrator:
    """ScServerRegistrator registers and unregisters modules"""

    def __init__(self, modules: ScServer):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._modules = modules
        self.is_registered = False

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self) -> None:
        self.is_registered = True
        self._register()

    def stop(self) -> None:
        self.is_registered = False
        self._unregister()

    @staticmethod
    def register_modules(*modules: ScModule):
        if not client.is_connected():
            raise ConnectionError("Connection to the sc-server is not established")
        for module in modules:
            if not isinstance(module, ScModule):
                raise TypeError("All elements of the module list must be ScModule instances")
            module.try_register()

    @staticmethod
    def unregister_modules(*modules: ScModule):
        if not client.is_connected():
            # TODO: How to unregister agents without connection?
            raise ConnectionError("Connection to the sc-server is not established")
        for module in modules:
            module.unregister()

    def _register(self) -> None:
        self.register_modules(*self._modules)

    def _unregister(self) -> None:
        self.unregister_modules(*self._modules)
