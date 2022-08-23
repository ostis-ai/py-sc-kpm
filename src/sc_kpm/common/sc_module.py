"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List

from sc_client import client

from sc_kpm.common.sc_agent import ScAgent

logger = logging.getLogger(__name__)

RegisterParams = namedtuple("RegisterParams", "ScAgent element event_type")


class ScModuleAbstract(ABC):
    @abstractmethod
    def register(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def unregister(self) -> None:
        raise NotImplementedError


class ScModule(ScModuleAbstract):
    params: List[RegisterParams] = []
    _agents: List[ScAgent] = []

    def register(self) -> None:
        if not self._agents:
            if client.is_connected():
                for param in self.params:
                    if not isinstance(param, RegisterParams):
                        raise TypeError("All elements of the module params list must be RegisterParams instance")
                    agent = param.ScAgent()
                    agent.register(param.element, param.event_type)
                    self._agents.append(agent)
                logger.debug("%s is registered", self.__class__.__name__)
            else:
                raise RuntimeError("Cannot register agents: connection to the sc-server is not established")

    def unregister(self) -> None:
        for agent in self._agents:
            agent.unregister()
        self._agents.clear()
        logger.debug("%s is unregistered", self.__class__.__name__)
