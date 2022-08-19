"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from sc_client import client

from sc_kpm.common.sc_agent import ScAgent

logger = logging.getLogger(__name__)


class ScModuleAbstract(ABC):
    @abstractmethod
    def register(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def unregister(self) -> None:
        raise NotImplementedError


class ScModule(ScModuleAbstract):
    agents: List[ScAgent] = []

    def __init__(self):
        self._is_registered = False

    def register(self) -> None:
        if not self._is_registered:
            if client.is_connected():
                for agent in self.agents:
                    if not isinstance(agent, ScAgent):
                        raise TypeError("All elements of the module agents list must be agents")
                    agent.register()
                self._is_registered = True
                logger.debug("%s is registered", self.__class__.__name__)
            else:
                raise RuntimeError("Cannot register agents: connection to the sc-server is not established")

    def unregister(self) -> None:
        for agent in self.agents:
            agent.unregister()
        self._is_registered = False
        logger.debug("%s is unregistered", self.__class__.__name__)
