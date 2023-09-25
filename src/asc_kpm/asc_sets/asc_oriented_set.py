from typing import Iterator, List, Optional

from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScTemplate, ScTemplateResult

from asc_kpm.asc_keynodes_ import asc_keynodes
from asc_kpm.asc_sets.asc_set import AScSet
from asc_kpm.utils.aio_common_utils import create_edge, create_role_relation, search_role_relation_template
from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_keynodes_ import sc_keynodes


class AScOrientedSet(AScSet):
    """
    ScOrientedSet is a class for handling oriented set structure in kb.

    It has main set_node and edged elements:
    Edge to the first element marked with 'rrel_1' node.
    The other have edges between edges from set_node marked with 'nrel_basic_sequence'.
    """

    async def add(self, *elements: ScAddr) -> None:
        """Add elements to ScOrientedSet"""
        if elements:
            elements_iterator = iter(elements)
            current_edge = (
                self._create_first_element_edge(next(elements_iterator))
                if self.is_empty()
                else self._get_last_edge_and_delete_rrel_last()
            )
            for element in elements_iterator:
                current_edge = await self._create_next_edge(current_edge, element)
            await self._mark_edge_with_rrel_last(current_edge)

    async def __aiter__(self) -> Iterator[ScAddr]:
        """Iterate by ScOrientedSet elements"""
        start_template = await search_role_relation_template(
            self._set_node, await asc_keynodes.get_valid(CommonIdentifiers.RREL_ONE)
        )
        if not start_template:
            return
        yield start_template.get(ScAlias.ELEMENT)
        next_edge = start_template.get(ScAlias.ACCESS_EDGE)
        while True:
            elem_search_result = await self._search_next_element_template(next_edge)
            if elem_search_result is None:
                return
            yield elem_search_result.get(ScAlias.ELEMENT)
            next_edge = elem_search_result.get(ScAlias.ACCESS_EDGE)

    @property
    async def elements_list(self) -> List[ScAddr]:
        """List of elements with order"""
        return [el async for el in self]

    async def remove(self, *elements: ScAddr) -> None:
        """Clear and add existing elements without given ones"""
        # TODO: optimize
        elements_new = [element for element in await self.elements_list if element not in elements]
        await self.clear()
        await self.add(*elements_new)

    async def _create_first_element_edge(self, element: ScAddr) -> ScAddr:
        """Create marked with rrel_1 edge to first element"""
        return await create_role_relation(
            self._set_node, element, await asc_keynodes.get_valid(CommonIdentifiers.RREL_ONE)
        )

    async def _get_last_edge_and_delete_rrel_last(self) -> Optional[ScAddr]:
        """Search last edge of ScOrientedSet is it exists"""
        # Search marked last edge
        template = ScTemplate()
        template.triple_with_relation(
            self._set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.ACCESS_EDGE,
            sc_types.UNKNOWN,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.RELATION_EDGE,
            await asc_keynodes.get_valid(CommonIdentifiers.RREL_LAST),
        )
        last_elem_templates = await asc_client.template_search(template)
        if last_elem_templates:
            last_elem_template = last_elem_templates[0]
            await asc_client.delete_elements(
                last_elem_template.get(ScAlias.RELATION_EDGE)
            )  # Delete edge between rrel_last and edge
            return last_elem_template.get(ScAlias.ACCESS_EDGE)

        # Search unmarked last edge
        next_elem_result = await search_role_relation_template(
            self._set_node, await asc_keynodes.get_valid(CommonIdentifiers.RREL_ONE)
        )
        while True:
            next_edge = next_elem_result.get(ScAlias.ACCESS_EDGE)
            next_elem_result = await self._search_next_element_template(next_edge)
            if next_elem_result is None:
                return next_edge

    async def _create_next_edge(self, previous_edge: ScAddr, element: ScAddr) -> ScAddr:
        """Create edge to element and connect with previous edge"""
        template = ScTemplate()
        template.triple(
            self._set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.ACCESS_EDGE,
            element,
        )
        template.triple_with_relation(
            previous_edge,
            sc_types.EDGE_D_COMMON_VAR,
            ScAlias.ACCESS_EDGE,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
        )
        return (await asc_client.template_generate(template)).get(ScAlias.ACCESS_EDGE)

    @staticmethod
    async def _mark_edge_with_rrel_last(last_edge: ScAddr) -> None:
        await create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM, await asc_keynodes.get_valid(CommonIdentifiers.RREL_LAST), last_edge
        )

    async def _search_next_element_template(self, cur_element_edge: ScAddr) -> Optional[ScTemplateResult]:
        templ = ScTemplate()
        templ.triple_with_relation(
            cur_element_edge,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.ACCESS_EDGE,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            await asc_keynodes.get_valid(CommonIdentifiers.NREL_BASIC_SEQUENCE),
        )
        templ.triple(self._set_node, ScAlias.ACCESS_EDGE, sc_types.UNKNOWN >> ScAlias.ELEMENT)
        search_results = await asc_client.template_search(templ)
        return search_results[0] if search_results else None
