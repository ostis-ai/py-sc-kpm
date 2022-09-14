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

from sc_kpm.constants import LOGGER_NAME
from sc_kpm.identifiers import QuestionStatus
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf
from sc_kpm.utils.action_utils import check_action_class


class ScAgentAbstract(ABC):
    def __init__(self, event_class: ScAddr, event_type: ScEventType):
        self._logger = logging.getLogger(LOGGER_NAME)
        self._event_class = event_class
        self._event_type = event_type
        self._event: ScEvent = None

    @abstractmethod
    def __repr__(self):
        pass

    def _register(self) -> None:
        if self._event is not None:
            self._logger.warning("Agent's almost registered")
            return
        event_params = ScEventParams(self._event_class, self._event_type, self._callback)
        self._event = client.events_create(event_params)[0]
        self._logger.info("Agent's registered with event type: %s", repr(self._event_type))

    def _unregister(self) -> None:
        if self._event is not None:
            client.events_destroy(self._event)
            self._event = None
            self._logger.info("Event's destroyed")
        else:
            self._logger.warning("Event's already destroyed or not registered")
        self._logger.info("Agent's unregistered")

    def _callback(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
        return self.on_event(init_element, init_edge, action_element)

    @abstractmethod
    def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
        pass


class ScAgent(ScAgentAbstract, ABC):
    def __init__(self, event_class: Union[Idtf, ScAddr], event_type: ScEventType):
        self._keynodes = ScKeynodes()
        if isinstance(event_class, Idtf):
            event_class = self._keynodes.resolve(event_class, sc_types.NODE_CONST_CLASS)
        if not event_class.is_valid():
            raise InvalidValueError("Element with provided address does not exist.")
        super().__init__(event_class, event_type)

    def __repr__(self):
        return f"ScAgent(event_class='{get_system_idtf(self._event_class)}', event_type={repr(self._event_type)})"


class ScAgentClassic(ScAgentAbstract, ABC):
    def __init__(self, action_class_name: Idtf, event_type: ScEventType = ScEventType.ADD_OUTGOING_EDGE):
        self._keynodes = ScKeynodes()
        super().__init__(
            event_class=self._keynodes[QuestionStatus.QUESTION_INITIATED.value],
            event_type=event_type,
        )
        self._action_class = self._keynodes.resolve(action_class_name, sc_types.NODE_CONST_CLASS)

    def __repr__(self):
        event_type_repr = (
            "" if self._event_type == ScEventType.ADD_OUTGOING_EDGE else f", event_type={repr(self._event_type)}"
        )
        return f"ClassicScAgent(action_class_name='{get_system_idtf(self._event_class)}{event_type_repr}')"

    def _confirm_action_class(self, action_node: ScAddr) -> bool:
        return check_action_class(self._action_class, action_node)

    @abstractmethod
    def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_node: ScAddr) -> ScResult:
        # pylint: disable=arguments-renamed
        pass
