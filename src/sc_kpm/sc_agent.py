"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod
from typing import Union

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_kpm.identifiers import QuestionStatus
from sc_kpm.logging import get_kpm_logger
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf
from sc_kpm.utils.action_utils import check_action_class

_logger = get_kpm_logger()


class ScAgentAbstract(ABC):
    def __init__(self, event_class: ScAddr, event_type: ScEventType):
        self._event_class = event_class
        self._event_type = event_type
        self._event: ScEvent = None

    @abstractmethod
    def __repr__(self):
        pass

    def _register(self) -> None:
        if self._event is not None:
            _logger.warning("%s is almost registered", self.__class__.__name__)
            return
        event_params = ScEventParams(self._event_class, self._event_type, self._callback)
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
            _logger.error("%s failed to create: event_class is invalid", self.__class__.__name__)
            raise InvalidValueError(f"event_class of {self.__class__.__name__} is invalid")
        super().__init__(event_class, event_type)

    def __repr__(self):
        return f"ScAgent(event_class='{get_system_idtf(self._event_class)}', event_type={repr(self._event_type)})"


class ScAgentClassic(ScAgent, ABC):
    def __init__(
        self,
        action_class_name: Idtf,
        event_class: Union[Idtf, ScAddr] = QuestionStatus.QUESTION_INITIATED.value,
        event_type: ScEventType = ScEventType.ADD_OUTGOING_EDGE,
    ):
        super().__init__(event_class, event_type)
        self._action_class_name = action_class_name
        self._action_class = self._keynodes.resolve(action_class_name, sc_types.NODE_CONST_CLASS)

    def __repr__(self):
        description = f"ClassicScAgent(action_class_name={repr(self._action_class_name)}"
        if self._event_class != self._keynodes.get(QuestionStatus.QUESTION_INITIATED.value):
            description = f"{description}, event_class={repr(get_system_idtf(self._event_class))}"
        if self._event_type != ScEventType.ADD_OUTGOING_EDGE:
            description = f"{description}, event_type={repr(self._event_type)}"
        return description + ")"

    def _confirm_action_class(self, action_element: ScAddr) -> bool:
        return check_action_class(self._action_class, action_element)
