"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional, Union

from sc_client import client
from sc_client.constants import sc_type
from sc_client.constants.common import ScEventType
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScEventSubscription, ScEventSubscriptionParams

from sc_kpm.identifiers import ActionStatus
from sc_kpm.sc_keynodes import Idtf, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils.action_utils import check_action_class


class ScAgentAbstract(ABC):
    def __init__(self, event_element: ScAddr, event_type: ScEventType) -> None:
        self._event_element = event_element
        self._event_type = event_type
        self._event: Optional[ScEventSubscription] = None
        self.logger = getLogger(f"{self.__module__}.{self.__class__.__name__}")

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def _register(self) -> None:
        if self._event is not None:
            self.logger.warning("Almost registered")
            return
        event_params = ScEventSubscriptionParams(self._event_element, self._event_type, self._callback)
        self._event = client.create_elementary_event_subscriptions(event_params)[0]
        self.logger.info(
            "Registered with ScEvent: %s - %s",
            repr(self._event_element),
            repr(self._event_type),
        )

    def _unregister(self) -> None:
        if self._event is None:
            self.logger.warning("ScEvent was already destroyed or not registered")
            return
        client.destroy_elementary_event_subscriptions(self._event)
        self._event = None
        self.logger.info(
            "Unregistered ScEvent: %s - %s",
            repr(self._event_element),
            repr(self._event_type),
        )

    def _callback(self, event_element: ScAddr, event_connector: ScAddr, action_element: ScAddr) -> ScResult:
        return self.on_event(event_element, event_connector, action_element)

    @abstractmethod
    def on_event(self, event_element: ScAddr, event_connector: ScAddr, action_element: ScAddr) -> ScResult:
        pass


class ScAgent(ScAgentAbstract, ABC):
    def __init__(self, event_element: Union[Idtf, ScAddr], event_type: ScEventType) -> None:
        if isinstance(event_element, Idtf):
            event_element = ScKeynodes.resolve(event_element, sc_type.CONST_NODE_CLASS)
        if not event_element.is_valid():
            self.logger.error("Failed to initialize ScAgent: event_class is invalid")
            raise InvalidValueError(f"event_class of {self.__class__.__name__} is invalid")
        super().__init__(event_element, event_type)

    def __repr__(self) -> str:
        return f"ScAgent(event_class='{self._event_element}', event_type={repr(self._event_type)})"


class ScAgentClassic(ScAgent, ABC):
    def __init__(
        self,
        action_class_name: Idtf,
        event_element: Union[Idtf, ScAddr] = ActionStatus.ACTION_INITIATED,
        event_type: ScEventType = ScEventType.AFTER_GENERATE_OUTGOING_ARC,
    ) -> None:
        super().__init__(event_element, event_type)
        self._action_class_name = action_class_name
        self._action_class = ScKeynodes.resolve(action_class_name, sc_type.CONST_NODE_CLASS)

    def __repr__(self) -> str:
        description = f"ClassicScAgent(action_class_name={repr(self._action_class_name)}"
        if self._event_element != ScKeynodes.get(ActionStatus.ACTION_INITIATED):
            description = f"{description}, event_class={repr(self._event_element)}"
        if self._event_type != ScEventType.AFTER_GENERATE_OUTGOING_ARC:
            description = f"{description}, event_type={repr(self._event_type)}"
        return description + ")"

    def _callback(self, event_element: ScAddr, event_connector: ScAddr, action_element: ScAddr) -> ScResult:
        if not check_action_class(self._action_class, action_element):
            return ScResult.SKIP
        self.logger.info("Confirmed action class")
        return self.on_event(event_element, event_connector, action_element)
