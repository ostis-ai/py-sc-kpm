from abc import ABC, abstractmethod
from typing import List

from sc_client.client import template_search
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate, ScTemplateResult


class ScSetAbstract(ABC):
    def __init__(self, set_node: ScAddr) -> None:
        self._set_node = set_node

    @property
    def set_node(self) -> ScAddr:
        """Get main element of sc-set"""
        return self._set_node

    def __len__(self) -> int:
        """Get sc-set power"""
        return len(self._elements_search_results())

    def __bool__(self) -> bool:
        """Check sc-set is not empty"""
        return bool(self._elements_search_results())

    def _elements_search_results(self) -> List[ScTemplateResult]:
        templ = ScTemplate()
        templ.triple(self._set_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.UNKNOWN)
        return template_search(templ)

    @abstractmethod
    def add(self, *elements: ScAddr) -> None:
        """Add elements to sc-set"""

    @property
    @abstractmethod
    def elements(self) -> List[ScAddr]:
        """Get all elements from sc-set"""
