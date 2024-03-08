from __future__ import annotations

from typing import Iterator

from sc_client import ScType
from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScConstruction, ScTemplate, ScTemplateResult

from asc_kpm.utils.aio_common_utils import create_node


class AScSet:
    """
    ScSet is a class for handling set construction in kb.

    It has main set_node and edged elements.
    """

    def __init__(self, set_node: ScAddr) -> None:
        self._set_node = set_node

    @classmethod
    async def create(cls, *elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None):
        if set_node is None:
            if set_node_type is None:
                set_node_type = sc_types.NODE_CONST
            set_node = await create_node(set_node_type)
        sc_set = cls(set_node)
        await sc_set.add(*elements)
        return sc_set

    async def add(self, *elements: ScAddr) -> None:
        """Add elements to ScSet"""
        if elements:
            construction = ScConstruction()
            for element in elements:
                construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, self._set_node, element)
            await asc_client.create_elements(construction)

    @property
    def set_node(self) -> ScAddr:
        """Get the main element of ScSet"""
        return self._set_node

    def __eq__(self, other: AScSet) -> bool:
        return self._set_node == other._set_node

    @property
    async def elements_set(self) -> set[ScAddr]:
        """Set of elements without order and duplicates"""
        search_results = await self._elements_search_results()
        elements = {result[2] for result in search_results}
        return elements

    async def len(self) -> int:
        """Get ScSet power"""
        return len(await self.elements_set)  # No duplicates

    async def is_empty(self) -> bool:
        """Check if ScSet doesn't contain any element"""
        return not bool(await self._elements_search_results())

    async def __aiter__(self) -> Iterator[ScAddr]:
        """Iterate by ScSet elements"""
        for element in await self.elements_set:
            yield element

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def contains(self, element: ScAddr) -> bool:
        """Check if ScSet contains element"""
        return element in await self.elements_set

    async def remove(self, *elements: ScAddr) -> None:
        """Remove the connections between set_node and elements"""
        templ = ScTemplate()
        for element in elements:
            templ.triple(self._set_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, element)
        template_results = await asc_client.template_search(templ)
        await asc_client.delete_elements(*(res[1] for res in template_results))

    async def clear(self) -> None:
        """Remove the connections between set_node and all elements"""
        template_results = await self._elements_search_results()
        await asc_client.delete_elements(*(res[1] for res in template_results))

    async def _elements_search_results(self) -> list[ScTemplateResult]:
        """Template search of all elements"""
        templ = ScTemplate()
        templ.triple(self._set_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.UNKNOWN)
        return await asc_client.template_search(templ)
