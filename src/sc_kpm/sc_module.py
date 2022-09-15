"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from sc_kpm.constants import MAIN_LOGGER
from sc_kpm.sc_agent import ScAgentAbstract


class ScModuleAbstract(ABC):
    @abstractmethod
    def _try_register(self) -> None:
        pass

    @abstractmethod
    def _unregister(self) -> None:
        pass


class ScModule(ScModuleAbstract):
    def __init__(self, *reg_agents):
        self._logger = logging.getLogger(MAIN_LOGGER)
        self._agents: List[ScAgentAbstract] = []
        self._reg_agents: List[ScAgentAbstract] = []
        self._reg_agents.extend(reg_agents)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self._reg_agents)[1:-1]})"

    def add_agent(self, agent: ScAgentAbstract) -> None:
        if self.is_registered():
            self._logger.warning("Agent %s wasn't added: module is already registered", repr(agent))
            return
        self._reg_agents.append(agent)

    def _try_register(self) -> None:
        if self.is_registered():
            self._logger.warning("Module failed to register: module is already registered")
            return
        if not self._reg_agents:
            self._logger.warning("Module failed to register: no register params")
            return
        for agent in self._reg_agents:
            agent._register()  # pylint: disable=protected-access
            self._agents.append(agent)
        self._reg_agents.clear()
        self._logger.info("Module's registered")

    def is_registered(self) -> bool:
        return bool(self._agents)

    def _unregister(self) -> None:
        for agent in self._agents:
            agent._unregister()  # pylint: disable=protected-access
        self._reg_agents.extend(self._agents)
        self._agents.clear()
        self._logger.info("Module's unregistered")
