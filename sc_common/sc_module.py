"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from abc import ABC
from typing import List, Set

from sc_client import client

from sc_common.sc_agent import ScAgent


class ScModule(ABC):
    agents: List[ScAgent] = []

    def __init__(self):
        _current_modules.add(self)

    def register(self) -> None:
        if client.is_connected():
            for agent in self.agents:
                if not isinstance(agent, ScAgent):
                    raise TypeError("All elements of the module agents list must be agents")
                agent.register()
            print(f"{self.__class__.__name__} is registred")
        else:
            raise RuntimeError("Cannot register agents: connection to the sc-server is not established")

    def unregister(self) -> None:
        for agent in self.agents:
            agent.unregister()
        print(f"{self.__class__.__name__} is unregistred")


_current_modules: Set[ScModule] = set()


def register_sc_modules():
    for module in _current_modules:
        module.register()


def unregister_sc_modules():
    for module in _current_modules:
        module.unregister()
    _current_modules.clear()
