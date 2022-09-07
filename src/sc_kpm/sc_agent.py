"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from typing import Union

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_kpm.identifiers import QuestionStatus
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils.action_utils import check_action_class


class ScAgentAbstract(ABC):
    def __init__(self, event_class: ScAddr, event_type: ScEventType):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._event_class = event_class
        self._event_type = event_type
        self._event: ScEvent = None

    def register(self) -> None:
        if self._event is not None:
            self._logger.warning("Agent is almost registered")
            return
        event_params = ScEventParams(self._event_class, self._event_type, self.on_event)
        self._event = client.events_create(event_params)[0]
        self._logger.info("Agent is registered with event type: %s", self._event_type)

    def unregister(self) -> None:
        if self._event is not None:
            client.events_destroy(self._event)
            self._event = None
            self._logger.info("Event is destroyed")
        else:
            self._logger.warning("Event is already destroyed or not registered")
        self._logger.info("Agent is unregistered")

    @abstractmethod
    def on_event(self, class_node: ScAddr, edge: ScAddr, action_node: ScAddr) -> ScResult:
        pass


class ScAgent(ScAgentAbstract, ABC):
    def __init__(self, event_class: Union[Idtf, ScAddr], event_type: ScEventType):
        self._keynodes = ScKeynodes()
        if isinstance(event_class, Idtf):
            event_class = self._keynodes.resolve(event_class, sc_types.NODE_CONST_CLASS)
        if not event_class.is_valid():
            raise InvalidValueError("Element with provided address does not exist.")
        super().__init__(event_class, event_type)


class ClassicScAgent(ScAgentAbstract, ABC):
    def __init__(self, action_class_name: Idtf, event_type: ScEventType = ScEventType.ADD_OUTGOING_EDGE):
        self._keynodes = ScKeynodes()
        super().__init__(
            event_class=self._keynodes[QuestionStatus.QUESTION_INITIATED.value],
            event_type=event_type,
        )
        self._action_class = self._keynodes.resolve(action_class_name, sc_types.NODE_CONST_CLASS)

    def _confirm_action_class(self, action_node: ScAddr) -> bool:
        return check_action_class(self._action_class, action_node)
