"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

from __future__ import annotations

import multiprocessing
import time
from abc import ABC, abstractmethod

from sc_client import client

from sc_kpm import ScModule


class ScServerAbstract(ABC):
    @abstractmethod
    def add_modules(self, *modules: ScModule) -> ScServerAbstract:
        raise NotImplementedError

    @abstractmethod
    def remove_modules(self, *modules: ScModule) -> ScServerAbstract:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError


class ScServer(ScServerAbstract):
    def __init__(self, sc_server_url: str, ping_freq: float = 0.1) -> None:
        self.url = sc_server_url
        self.ping_freq = ping_freq
        self.modules: list[ScModule] = []
        self._server_process = None

    def add_modules(self, *modules: ScModule) -> ScServerAbstract:
        self.modules.extend(modules)
        self._register_sc_modules()
        return self

    def remove_modules(self, *modules: ScModule) -> ScServerAbstract:
        for module in modules:
            self.modules.remove(module)
        return self

    def _serve(self):
        while client.is_connected():
            time.sleep(self.ping_freq)

    def start(self) -> None:
        client.connect(self.url)
        self._server_process = multiprocessing.Process(target=self._serve)
        self._server_process.start()

    def stop(self):
        self._unregister_sc_modules()
        self._server_process.terminate()
        client.disconnect()
        self._clear_modules()

    def _register_sc_modules(self) -> None:
        for module in self.modules:
            if not isinstance(module, ScModule):
                raise TypeError("All elements of the module list must be ScModule instances")
            module.try_register()  # pylint: disable=protected-access

    def _unregister_sc_modules(self) -> None:
        for module in self.modules:
            module.unregister()  # pylint: disable=protected-access

    def _clear_modules(self):
        self.modules = []
