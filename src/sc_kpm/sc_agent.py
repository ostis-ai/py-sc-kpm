"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from typing import Union

from sc_client import client
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_kpm.sc_keynodes import ScKeynodes
from sc_kpm.sc_result import ScResult


class ScAgentAbstract(ABC):
    @abstractmethod
    def register(self, event_node: Union[str, ScAddr], event_type: ScEventType) -> None:
        pass

    @abstractmethod
    def unregister(self) -> None:
        pass

    @abstractmethod
    def on_event(self, class_node: ScAddr, edge: ScAddr, action_node: ScAddr) -> ScResult:
        pass


class ScAgent(ScAgentAbstract, ABC):
    def __init__(self):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._keynodes = ScKeynodes()
        self._event: ScEvent = None

    def register(self, event_node: Union[str, ScAddr], event_type: ScEventType) -> None:
        if self._event:
            self._logger.warning("Agent is almost registered")
            return
        if isinstance(event_node, str):
            event_node = self._keynodes[event_node]
        if not event_node.is_valid():
            raise InvalidValueError("Element with provided address does not exist.")
        event_params = ScEventParams(event_node, event_type, self.on_event)
        self._event = client.events_create(event_params)[0]
        self._logger.info("Agent is registered")

    def unregister(self) -> None:
        if isinstance(self._event, ScEvent):
            client.events_destroy(self._event)
            self._logger.info("Event is destroyed")
        else:
            self._logger.warning("Event is already destroyed or not registered")
        self._logger.info("Agent is unregistered")
