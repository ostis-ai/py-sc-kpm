"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from sc_kpm.sc_agent import ScAgentAbstract


class ScModuleAbstract(ABC):
    @abstractmethod
    def try_register(self) -> None:
        pass

    @abstractmethod
    def unregister(self) -> None:
        pass


class ScModule(ScModuleAbstract):
    def __init__(self):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._reg_agents: List[ScAgentAbstract] = []
        self._agents: List[ScAgentAbstract] = []

    def add_agent(self, agent: ScAgentAbstract) -> None:
        self._reg_agents.append(agent)

    def try_register(self) -> None:
        if not self._reg_agents:
            self._logger.warning("Module failed to register: no register params")
            return
        if self.is_registered():
            self._logger.warning("Module failed to register: module is already registered")
            return
        for agent in self._reg_agents:
            agent.register()
            self._agents.append(agent)
        self._reg_agents.clear()
        self._logger.info("Module is registered")

    def is_registered(self) -> bool:
        return bool(self._agents)

    def unregister(self) -> None:
        for agent in self._agents:
            agent.unregister()
        self._agents.clear()
        self._logger.info("Module is unregistered")
