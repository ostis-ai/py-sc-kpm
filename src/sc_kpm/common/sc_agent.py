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
    _event: ScEvent = None

    def register(self, element: Union[str, ScAddr] = ScAddr(0), event_type: ScEventType = ScEventType.UNKNOWN) -> None:
        def _callback(addr: ScAddr, edge_addr: ScAddr, other_addr: ScAddr) -> None:
            self.on_event(addr, edge_addr, other_addr)

        source_node_addr = ScKeynodes()[element] if isinstance(element, str) else element
        if source_node_addr is None:
            raise InvalidValueError("Element with provided address does not exist.")
        event_params = ScEventParams(source_node_addr, event_type, _callback)
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
