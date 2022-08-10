"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod

from sc_client import client
from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_common.sc_keynodes import ScKeynodes


class ScAgent(ABC):
    source_node_idtf: str = None
    event_type: ScEventType = None

    def __init__(self):
        self.keynodes = ScKeynodes()
        self._event = None

    def _register(self) -> None:
        event_params = ScEventParams(self.keynodes[self.source_node_idtf], self.event_type, self.on_event)
        sc_event = client.events_create(event_params)
        self._event = sc_event[0]
        print(f"{self.__class__.__name__} is registred")

    def _unregister(self) -> None:
        if isinstance(self._event, ScEvent):
            client.events_destroy(self._event)
            print(f"{self.__class__.__name__} event was destroyed")
        print(f"{self.__class__.__name__} is unregistred")

    @staticmethod
    @abstractmethod
    def on_event(source_node: ScAddr, edge: ScAddr, target_node: ScAddr) -> None:
        pass
