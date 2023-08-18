from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Union

from sc_client.constants.common import ScEventType
from sc_client.models.sc_addr import ScAddr

ScEventCallbackFuncSync = Callable[[ScAddr, ScAddr, ScAddr], None]
ScEventCallbackFuncAsync = Callable[[ScAddr, ScAddr, ScAddr], Coroutine[Any, Any, None]]
ScEventCallbackFunc = Union[ScEventCallbackFuncSync, ScEventCallbackFuncAsync]


@dataclass
class ScEventParams:
    addr: ScAddr
    event_type: ScEventType
    callback: ScEventCallbackFunc


@dataclass
class ScEvent:
    id: int = 0
    event_type: ScEventType = None
    callback: ScEventCallbackFunc = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, event_type={self.event_type})"
