from typing import Iterator, List

from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScTemplate

from asc_kpm.asc_keynodes_ import asc_keynodes
from asc_kpm.asc_sets.asc_set import AScSet


class AScNumberedSet(AScSet):
    """
    ScNumberedSet is a class for handling numbered set structure in kb.

    It has main set_node and edged elements:
    Edge to each element marked with 'rrel_1', 'rrel_2', and so on nodes.
    """

    async def add(self, *elements: ScAddr) -> None:
        """Add elements to ScNumberedSet"""
        if elements:
            template = ScTemplate()
            for index, element in enumerate(elements, await self.len() + 1):
                template.triple_with_relation(
                    self._set_node,
                    sc_types.EDGE_ACCESS_VAR_POS_PERM,
                    element,
                    sc_types.EDGE_ACCESS_VAR_POS_PERM,
                    await asc_keynodes.rrel_index(index),
                )
            await asc_client.template_generate(template)

    async def __aiter__(self) -> Iterator[ScAddr]:
        for element in await self.elements_list:
            yield element

    @property
    async def elements_list(self) -> List[ScAddr]:
        """Iterate by ScNumberedSet elements"""
        templ = ScTemplate()
        templ.triple_with_relation(
            self._set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.UNKNOWN,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_ROLE,
        )
        results = await asc_client.template_search(templ)
        sorted_results = sorted((result for result in results), key=lambda res: res[4].value)
        # Sort rrel elements addrs
        return [result[2] for result in sorted_results]

    async def at(self, i: int) -> ScAddr:
        templ = ScTemplate()
        templ.triple_with_relation(
            self._set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.UNKNOWN,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            await asc_keynodes.rrel_index(i + 1),
        )
        results = await asc_client.template_search(templ)
        if not results:
            raise KeyError("No element by index")
        return results[0][2]

    async def remove(self, *elements: ScAddr) -> None:
        """Clear and add existing elements without given ones"""
        # TODO: optimize
        elements_new = [element for element in await self.elements_list if element not in elements]
        await self.clear()
        await self.add(*elements_new)
