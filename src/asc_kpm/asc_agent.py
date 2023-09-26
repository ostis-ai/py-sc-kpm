"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import logging
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional, Union

from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import AScEventParams, ScAddr, ScEvent
from sc_client.sc_exceptions import InvalidValueError

from asc_kpm.asc_keynodes_ import Idtf, asc_keynodes
from asc_kpm.utils.aio_action_utils import check_action_class
from sc_kpm.identifiers import QuestionStatus
from sc_kpm.sc_result import ScResult


class AScAgentAbstract(ABC):
    logger: logging.Logger

    def __init__(self, event_element: ScAddr, event_type: ScEventType) -> None:
        self._event_element = event_element
        self._event_type = event_type
        self._event: Optional[ScEvent] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    async def _register(self) -> None:
        if self._event is not None:
            self.logger.warning("Almost registered")
            return
        event_params = AScEventParams(self._event_element, self._event_type, self._callback)
        self._event = (await asc_client.events_create(event_params))[0]
        self.logger.info("Registered with ScEvent: %s - %s", repr(self._event_element), repr(self._event_type))

    async def _unregister(self) -> None:
        if self._event is None:
            self.logger.warning("ScEvent was already destroyed or not registered")
            return
        await asc_client.events_destroy(self._event)
        self._event = None
        self.logger.info("Unregistered ScEvent: %s - %s", repr(self._event_element), repr(self._event_type))

    async def _callback(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr):
        result = await self.on_event(event_element, event_edge, action_element)
        self.logger.info(result)

    @abstractmethod
    async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        pass


class AScAgent(AScAgentAbstract, ABC):
    @classmethod
    async def ainit(cls, event_element: Union[Idtf, ScAddr], event_type: ScEventType):
        if isinstance(event_element, Idtf):
            event_element = await asc_keynodes.resolve(event_element, sc_types.NODE_CONST_CLASS)
        cls.logger = getLogger(f"{cls.__module__}.{cls.__name__}")
        if not event_element.is_valid():
            cls.logger.error("Failed to initialize ScAgent: event_class is invalid")
            raise InvalidValueError(f"event_class of {cls.__name__} is invalid")
        return cls(event_element, event_type)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(event_class='{self._event_element}', event_type={repr(self._event_type)})"


class AScAgentClassic(AScAgent, ABC):
    _action_class_name: Idtf
    _action_class: ScAddr

    # pylint: disable=protected-access
    # pylint: disable=arguments-differ
    @classmethod
    async def ainit(
        cls,
        action_class_name: Idtf,
        event_element: Union[Idtf, ScAddr] = QuestionStatus.QUESTION_INITIATED,
        event_type: ScEventType = ScEventType.ADD_OUTGOING_EDGE,
    ):
        instance = await super().ainit(event_element, event_type)
        instance._action_class_name = action_class_name
        instance._action_class = await asc_keynodes.resolve(action_class_name, sc_types.NODE_CONST_CLASS)
        return instance

    async def _callback(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        if not await check_action_class(self._action_class, action_element):
            return ScResult.SKIP
        self.logger.info("Confirmed action class")
        return await self.on_event(event_element, event_edge, action_element)
