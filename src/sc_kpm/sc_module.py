"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Type, Union

from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr

from sc_kpm.identifiers import QuestionStatus
from sc_kpm.sc_agent import ScAgentAbstract


@dataclass
class RegisterParams:
    agent: Type[ScAgentAbstract]
    action_node: Union[str, ScAddr]
    event_type: ScEventType


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
        self._reg_params: List[RegisterParams] = []
        self._agents: List[ScAgentAbstract] = []

    def add_agent(
        self,
        agent: Type[ScAgentAbstract],
        action_node: Union[str, ScAddr] = QuestionStatus.QUESTION_INITIATED.value,
        event_type: ScEventType = ScEventType.ADD_OUTGOING_EDGE,
    ) -> None:
        self._reg_params.append(RegisterParams(agent, action_node, event_type))

    def try_register(self) -> None:
        if not self._reg_params:
            self._logger.warning("Module failed to register: no register params")
            return
        if self.is_registered():
            self._logger.warning("Module failed to register: module is already registered")
            return
        for params in self._reg_params:
            if not isinstance(params, RegisterParams):
                raise TypeError("All elements of the module params list must be RegisterParams instance")
            agent = params.agent()
            agent.register(params.action_node, params.event_type)
            self._agents.append(agent)
        self._reg_params.clear()
        self._logger.info("Module is registered")

    def is_registered(self) -> bool:
        return bool(self._agents)

    def unregister(self) -> None:
        for agent in self._agents:
            agent.unregister()
        self._agents.clear()
        self._logger.info("Module is unregistered")
