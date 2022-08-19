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

from sc_kpm.common.sc_keynodes import ScKeynodes
from sc_kpm.common.sc_result import ScResult

logger = logging.getLogger(__name__)


class ScAgentAbstract(ABC):
    def __init__(self, source_node: Union[str, ScAddr] = ScAddr(0), event_type: ScEventType = ScEventType.UNKNOWN):
        self.source_node = source_node
        self.event_type = event_type
        self.keynodes = ScKeynodes()
        self._event = None

    def register(self) -> None:
        def _callback(addr: ScAddr, edge_addr: ScAddr, other_addr: ScAddr) -> None:
            self.on_event(addr, edge_addr, other_addr)

        source_node_addr = self.keynodes[self.source_node] if isinstance(self.source_node, str) else self.source_node
        if source_node_addr is None:
            raise InvalidValueError("Element with provided address does not exist.")
        event_params = ScEventParams(source_node_addr, self.event_type, _callback)
        sc_event = client.events_create(event_params)
        self._event = sc_event[0]
        logger.debug("%s is registered", self.__class__.__name__)

    def unregister(self) -> None:
        if isinstance(self._event, ScEvent):
            client.events_destroy(self._event)
            logger.debug("%s event is destroyed", self.__class__.__name__)
        logger.debug("%s is unregistered", self.__class__.__name__)

    @abstractmethod
    def on_event(self, source_node: ScAddr, edge: ScAddr, target_node: ScAddr) -> ScResult:
        raise NotImplementedError


class ScAgent(ScAgentAbstract):
    @abstractmethod
    def on_event(self, source_node: ScAddr, edge: ScAddr, target_node: ScAddr) -> ScResult:
        raise NotImplementedError
