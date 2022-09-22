"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod
from typing import List

from sc_kpm.logging import get_kpm_logger
from sc_kpm.sc_agent import ScAgentAbstract

_logger = get_kpm_logger()


class ScModuleAbstract(ABC):
    """
    ScModule is a container for handling multiple ScAgent objects.
    You can add and remove agents while module is registered or unregistered.
    """

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def add_agent(self, agent: ScAgentAbstract) -> None:
        """Add agent to the module and register it if module is registered"""

    @abstractmethod
    def remove_agent(self, agent: ScAgentAbstract) -> None:
        """Remove agent from the module and unregister it if module is registered"""

    @abstractmethod
    def _register(self) -> None:
        """Register all agents in the module"""

    @abstractmethod
    def _unregister(self) -> None:
        """Unregister all agents from the module"""


class ScModule(ScModuleAbstract):
    def __init__(self, *agents: ScAgentAbstract) -> None:
        self._agents: List[ScAgentAbstract] = []
        self._agents.extend(agents)
        self._is_registered: bool = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(repr, self._agents))})"

    def add_agent(self, agent: ScAgentAbstract) -> None:
        if self._is_registered:
            agent._register()  # pylint: disable=protected-access
        self._agents.append(agent)

    def remove_agent(self, agent: ScAgentAbstract) -> None:
        if self._is_registered:
            agent._unregister()  # pylint: disable=protected-access
        self._agents.remove(agent)

    def _register(self) -> None:
        if self._is_registered:
            _logger.warning("%s failed to register: module is already registered", self.__class__.__name__)
            return
        if not self._agents:
            _logger.warning("No agents to register in %s", self.__class__.__name__)
        for agent in self._agents:
            agent._register()  # pylint: disable=protected-access
        self._is_registered = True
        _logger.info("%s was registered", self.__class__.__name__)

    def _unregister(self) -> None:
        for agent in self._agents:
            agent._unregister()  # pylint: disable=protected-access
        self._is_registered = False
        _logger.info("%s was unregistered", self.__class__.__name__)
