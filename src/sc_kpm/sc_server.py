"""
This source file is part of an OSTIS project. For the latest info, see https:#github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https:#opensource.org/licenses/MIT)
"""

import threading
import time
from abc import ABC, abstractmethod
from typing import List

from sc_client import client

from sc_kpm.sc_module import ScModule

PING_FREQ_DEFAULT: int = 1


class ScServerAbstract(ABC):
    @abstractmethod
    def add_modules(self, *modules: ScModule) -> None:
        pass

    @abstractmethod
    def remove_modules(self, *modules: ScModule) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


class ScServer(ScServerAbstract):
    def __init__(self, sc_server_url: str, ping_freq: int = PING_FREQ_DEFAULT):
        self.ping_freq = ping_freq
        self.modules: List[ScModule] = []
        self.is_active = False
        client.connect(sc_server_url)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def add_modules(self, *modules: ScModule) -> None:
        self.modules.extend(modules)
        self._register_sc_modules()

    def remove_modules(self, *modules: ScModule) -> None:
        for module in modules:
            self.modules.remove(module)

    def _serve(self) -> None:
        while client.is_connected() and self.is_active:
            time.sleep(self.ping_freq)
        self._unregister_sc_modules()
        self.modules.clear()

    def start(self) -> None:
        server_thread = threading.Thread(target=self._serve, name="sc-server-thread", daemon=True)
        self.is_active = True
        server_thread.start()

    def stop(self) -> None:
        self.is_active = False

    def _register_sc_modules(self) -> None:
        if not client.is_connected():
            raise ConnectionError("Connection to the sc-server is not established")
        for module in self.modules:
            if not isinstance(module, ScModule):
                raise TypeError("All elements of the module list must be ScModule instances")
            module.try_register()  # pylint: disable=protected-access

    def _unregister_sc_modules(self) -> None:
        for module in self.modules:
            module.unregister()  # pylint: disable=protected-access
