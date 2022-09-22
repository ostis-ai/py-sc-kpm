"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod
from typing import Optional, Union

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_kpm.identifiers import QuestionStatus
from sc_kpm.logging import get_kpm_logger
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils.action_utils import check_action_class

_logger = get_kpm_logger()


class ScAgentAbstract(ABC):
    def __init__(self, event_element: ScAddr, event_type: ScEventType) -> None:
        self._event_element = event_element
        self._event_type = event_type
        self._event: Optional[ScEvent] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def _register(self) -> None:
        if self._event is not None:
            _logger.warning("%s is almost registered", self.__class__.__name__)
            return
        event_params = ScEventParams(self._event_element, self._event_type, self._callback)
        self._event = client.events_create(event_params)[0]
        _logger.info("ScEvent of %s was registered, %s", self.__class__.__name__, repr(self._event_type))

    def _unregister(self) -> None:
        if self._event is not None:
            client.events_destroy(self._event)
            self._event = None
            _logger.info("ScEvent of %s was destroyed", self.__class__.__name__)
        else:
            _logger.warning("ScEvent of %s is already destroyed or not registered", self.__class__.__name__)
        _logger.info("%s was unregistered", self.__class__.__name__)

    def _callback(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        return self.on_event(event_element, event_edge, action_element)

    @abstractmethod
    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        pass


class ScAgent(ScAgentAbstract, ABC):
    def __init__(self, event_element: Union[Idtf, ScAddr], event_type: ScEventType) -> None:
        self._keynodes = ScKeynodes()
        if isinstance(event_element, Idtf):
            event_element = self._keynodes.resolve(event_element, sc_types.NODE_CONST_CLASS)
        if not event_element.is_valid():
            _logger.error("%s failed to create: event_class is invalid", self.__class__.__name__)
            raise InvalidValueError(f"event_class of {self.__class__.__name__} is invalid")
        super().__init__(event_element, event_type)

    def __repr__(self) -> str:
        return f"ScAgent(event_class='{self._event_element}', event_type={repr(self._event_type)})"


class ScAgentClassic(ScAgent, ABC):
    def __init__(
        self,
        action_class_name: Idtf,
        event_element: Union[Idtf, ScAddr] = QuestionStatus.QUESTION_INITIATED,
        event_type: ScEventType = ScEventType.ADD_OUTGOING_EDGE,
    ) -> None:
        super().__init__(event_element, event_type)
        self._action_class_name = action_class_name
        self._action_class = self._keynodes.resolve(action_class_name, sc_types.NODE_CONST_CLASS)

    def __repr__(self) -> str:
        description = f"ClassicScAgent(action_class_name={repr(self._action_class_name)}"
        if self._event_element != self._keynodes.get(QuestionStatus.QUESTION_INITIATED):
            description = f"{description}, event_class={repr(self._event_element)}"
        if self._event_type != ScEventType.ADD_OUTGOING_EDGE:
            description = f"{description}, event_type={repr(self._event_type)}"
        return description + ")"

    def _confirm_action_class(self, action_element: ScAddr) -> bool:
        return check_action_class(self._action_class, action_element)
