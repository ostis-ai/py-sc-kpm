from typing import Iterator, List, Optional

from sc_client.client import template_search
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate, ScTemplateResult

from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_sets.sc_set_abstract import ScSetAbstract
from sc_kpm.utils import (
    create_edge,
    create_node,
    create_norole_relation,
    create_role_relation,
    search_role_relation_template,
)


class ScOrientedSet(ScSetAbstract):
    def __init__(self, *elements: ScAddr, set_node: ScAddr = None) -> None:
        if set_node is None:
            set_node = create_node(sc_types.NODE_CONST)
        super().__init__(set_node)

        self.add(*elements)

    def add(self, *elements: ScAddr) -> None:
        if elements:
            elements_iterator = iter(elements)
            if self:
                current_edge = self._get_last_edge()
            else:
                current_edge = create_role_relation(self._set_node, next(elements_iterator), ScKeynodes.rrel(1))
            for next_element in elements_iterator:
                next_edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, self._set_node, next_element)
                create_norole_relation(current_edge, next_edge, ScKeynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE])
                current_edge = next_edge

    def _get_last_edge(self) -> Optional[ScAddr]:
        start_template = search_role_relation_template(self._set_node, ScKeynodes.rrel(1))
        next_edge = start_template.get(ScAlias.ACCESS_EDGE)
        while True:
            elem_search_result = self._search_next_element_template(next_edge)
            if elem_search_result is None:
                return next_edge
            next_edge = elem_search_result.get(ScAlias.ACCESS_EDGE)

    def _search_next_element_template(self, cur_element_edge: ScAddr) -> Optional[ScTemplateResult]:
        templ = ScTemplate()
        templ.triple_with_relation(
            cur_element_edge,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.ACCESS_EDGE,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
        )
        templ.triple(self._set_node, ScAlias.ACCESS_EDGE, sc_types.UNKNOWN >> ScAlias.ELEMENT)
        search_results = template_search(templ)
        if not search_results:
            return None
        return search_results[0]

    def __iter__(self) -> Iterator[ScAddr]:
        """Iterate by elements of oriented-sc-set"""
        start_template = search_role_relation_template(self._set_node, ScKeynodes.rrel(1))
        if not start_template:
            return
        yield start_template.get(ScAlias.ELEMENT)
        next_edge = start_template.get(ScAlias.ACCESS_EDGE)
        while True:
            elem_search_result = self._search_next_element_template(next_edge)
            if elem_search_result is None:
                return
            yield elem_search_result.get(ScAlias.ELEMENT)
            next_edge = elem_search_result.get(ScAlias.ACCESS_EDGE)

    @property
    def elements(self) -> List[ScAddr]:
        """Get all elements of oriented-sc-set"""
        return list(self)
