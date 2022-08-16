"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod
from typing import Union

from sc_client import client
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_kpm.common.sc_keynodes import ScKeynodes


class ScAgentAbstract(ABC):
    source_node: Union[str, ScAddr] = None
    event_type: ScEventType = None

    def __init__(self):
        self.keynodes = ScKeynodes()
        self._event = None
        self.setup()

    def register(self) -> None:
        source_node_addr = self.keynodes[self.source_node] if isinstance(self.source_node, str) else self.source_node
        if source_node_addr is None:
            raise InvalidValueError("Element with provided address does not exist.")
        event_params = ScEventParams(source_node_addr, self.event_type, self.on_event)
        sc_event = client.events_create(event_params)
        self._event = sc_event[0]
        print(f"{self.__class__.__name__} is registred")

    def unregister(self) -> None:
        if isinstance(self._event, ScEvent):
            client.events_destroy(self._event)
            print(f"{self.__class__.__name__} event was destroyed")
        print(f"{self.__class__.__name__} is unregistred")

    @classmethod
    @abstractmethod
    def setup(cls):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def on_event(source_node: ScAddr, edge: ScAddr, target_node: ScAddr) -> None:
        raise NotImplementedError


class ScAgent(ScAgentAbstract):
    @classmethod
    @abstractmethod
    def setup(cls):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def on_event(source_node: ScAddr, edge: ScAddr, target_node: ScAddr) -> None:
        raise NotImplementedError
