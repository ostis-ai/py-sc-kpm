"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import threading
import time
from abc import ABC
from typing import List

from sc_client import client

from sc_kpm.common.sc_agent import ScAgent


class ScModule(ABC):
    agents: List[ScAgent] = []

    def __init__(self):
        self.is_registred = False

    def register(self) -> None:
        if not self.is_registred:
            if client.is_connected():
                for agent in self.agents:
                    if not isinstance(agent, ScAgent):
                        raise TypeError("All elements of the module agents list must be agents")
                    agent.register()
                self.is_registred = True
                print(f"{self.__class__.__name__} is registred")
            else:
                raise RuntimeError("Cannot register agents: connection to the sc-server is not established")

    def unregister(self) -> None:
        for agent in self.agents:
            agent.unregister()
        self.is_registred = False
        print(f"{self.__class__.__name__} is unregistred")


class ScServer:
    def __init__(self, sc_server_url: str, ping_freq: int = 1) -> None:
        self.url = sc_server_url
        self.ping_freq = ping_freq
        self.modules: List[ScModule] = []
        self.is_active = False
        client.connect(sc_server_url)

    def add_modules(self, *modules: ScModule):
        self.modules.extend(modules)
        self._register_sc_modules()

    def remove_modules(self, *modules: ScModule):
        for module in modules:
            self.modules.remove(module)

    def _serve(self):
        while client.is_connected() and self.is_active:
            time.sleep(self.ping_freq)
            if len(self.modules) == 0:
                break
        self._unregister_sc_modules()
        self._clear_modules()

    def start(self, *modules: ScModule) -> None:
        self.add_modules(*modules)
        server_thread = threading.Thread(target=self._serve, name="sc-server-thread")
        server_thread.start()
        self.is_active = True

    def stop(self):
        self.is_active = False

    def _register_sc_modules(self) -> None:
        for module in self.modules:
            if not isinstance(module, ScModule):
                raise TypeError("All elements of the module list must be ScModule instances")
            module.register()

    def _unregister_sc_modules(self) -> None:
        for module in self.modules:
            module.unregister()

    def _clear_modules(self):
        self.modules = []
