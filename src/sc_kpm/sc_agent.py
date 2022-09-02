"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Union

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEvent, ScEventParams

from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import create_norole_relation, get_element_by_role_relation
from sc_kpm.utils.action_utils import check_action_class
from sc_kpm.utils.creation_utils import create_structure


class ScAgentAbstract(ABC):
    _event_class: ScAddr
    _event_type: ScEventType

    def __init__(self):
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")
        self._keynodes = ScKeynodes()
        self._event = None

    def register(self) -> None:
        if self._event:
            self._logger.warning("Agent is almost registered")
            return
        event_params = ScEventParams(self._event_class, self._event_type, self.on_event)
        self._event = client.events_create(event_params)[0]
        self._logger.info("Agent is registered")

    def unregister(self) -> None:
        if isinstance(self._event, ScEvent):
            client.events_destroy(self._event)
            self._logger.info("Event is destroyed")
        else:
            self._logger.warning("Event is already destroyed or not registered")
        self._logger.info("Agent is unregistered")

    @abstractmethod
    def on_event(self, class_node: ScAddr, edge: ScAddr, action_node: ScAddr) -> ScResult:
        pass


class ScAgent(ScAgentAbstract, ABC):
    def __init__(self, event_class: Union[Idtf, ScAddr], event_type: ScEventType):
        super().__init__()
        if isinstance(event_class, Idtf):
            event_class = self._keynodes[event_class]
        if not event_class.is_valid():
            raise InvalidValueError("Element with provided address does not exist.")
        self._event_class = event_class
        self._event_type = event_type


class ClassicScAgent(ScAgentAbstract, ABC):
    def __init__(self, action_class_name: Idtf):
        super().__init__()
        self._event_class = self._keynodes[QuestionStatus.QUESTION_INITIATED.value]
        self._event_type = ScEventType.ADD_OUTGOING_EDGE
        self._action_class = self._keynodes.resolve(action_class_name, sc_types.NODE_CONST_CLASS)

    def _confirm_action_class(self, action_node: ScAddr) -> bool:
        return check_action_class(self._action_class, action_node)

    def _get_arguments(self, action_node: ScAddr, count: int) -> List[ScAddr]:
        arguments = []
        for index in range(1, count + 1):
            rrel_i = self._keynodes[f"rrel_{index}"]
            argument = get_element_by_role_relation(action_node, rrel_i)
            if not argument.is_valid():
                self._logger.warning(f"Argument {index} is empty")
            arguments.append(argument)
        return arguments

    def _create_answer(self, action_node: ScAddr, *elements: ScAddr):
        answer_struct_node = create_structure(*elements)
        create_norole_relation(action_node, answer_struct_node, self._keynodes[CommonIdentifiers.NREL_ANSWER.value])
