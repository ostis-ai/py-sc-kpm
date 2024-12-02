from typing import Iterator, List, Optional

from sc_client.client import erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScTemplate, ScTemplateResult

from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_keynodes import ScKeynodes
from sc_kpm.sc_sets.sc_set import ScSet
from sc_kpm.utils.common_utils import generate_connector, generate_role_relation, search_role_relation_template


class ScOrientedSet(ScSet):
    """
    ScOrientedSet is a class for handling oriented set structure in kb.

    It has main set_node and arc elements:
    Arc to the first element marked with 'rrel_1' node.
    The other have arcs between arcs from set_node marked with 'nrel_basic_sequence'.
    """

    def add(self, *elements: ScAddr) -> None:
        """Add elements to ScOrientedSet"""
        if elements:
            elements_iterator = iter(elements)
            current_arc = (
                self._generate_first_element_arc(next(elements_iterator))
                if self.is_empty()
                else self._get_last_arc_and_erase_rrel_last()
            )
            for element in elements_iterator:
                current_arc = self._generate_next_arc(current_arc, element)
            self._mark_arc_with_rrel_last(current_arc)

    def __iter__(self) -> Iterator[ScAddr]:
        """Iterate by ScOrientedSet elements"""
        start_template = search_role_relation_template(self._set_node, ScKeynodes[CommonIdentifiers.RREL_ONE])
        if not start_template:
            return
        yield start_template.get(ScAlias.ELEMENT)
        next_arc = start_template.get(ScAlias.RELATION_ARC)
        while True:
            elem_search_result = self._search_next_element_template(next_arc)
            if elem_search_result is None:
                return
            yield elem_search_result.get(ScAlias.ELEMENT)
            next_arc = elem_search_result.get(ScAlias.RELATION_ARC)

    @property
    def elements_list(self) -> List[ScAddr]:
        """List of elements with order"""
        return list(self)

    def remove(self, *elements: ScAddr) -> None:
        """Clear and add existing elements without given ones"""
        # TODO: optimize
        elements_new = [element for element in self.elements_list if element not in elements]
        self.clear()
        self.add(*elements_new)

    def _generate_first_element_arc(self, element: ScAddr) -> ScAddr:
        """Generate marked with rrel_1 arc to first element"""
        return generate_role_relation(self._set_node, element, ScKeynodes[CommonIdentifiers.RREL_ONE])

    def _get_last_arc_and_erase_rrel_last(self) -> Optional[ScAddr]:
        """Search last arc of ScOrientedSet if it exists"""
        # Search marked last arc
        template = ScTemplate()
        template.quintuple(
            self._set_node,
            sc_type.VAR_PERM_POS_ARC >> ScAlias.MEMBERSHIP_ARC,
            sc_type.UNKNOWN,
            sc_type.VAR_PERM_POS_ARC >> ScAlias.RELATION_ARC,
            ScKeynodes[CommonIdentifiers.RREL_LAST],
        )
        last_elem_templates = search_by_template(template)
        if last_elem_templates:
            last_elem_template = last_elem_templates[0]
            erase_elements(last_elem_template.get(ScAlias.RELATION_ARC))  # Erase arc between rrel_last and arc
            return last_elem_template.get(ScAlias.MEMBERSHIP_ARC)

        # Search unmarked last arc
        next_elem_result = search_role_relation_template(self._set_node, ScKeynodes[CommonIdentifiers.RREL_ONE])
        while True:
            next_arc = next_elem_result.get(ScAlias.RELATION_ARC)
            next_elem_result = self._search_next_element_template(next_arc)
            if next_elem_result is None:
                return next_arc

    def _generate_next_arc(self, previous_arc: ScAddr, element: ScAddr) -> ScAddr:
        """Generate arc to element and connect with previous arc"""
        template = ScTemplate()
        template.triple(
            self._set_node,
            sc_type.VAR_PERM_POS_ARC >> ScAlias.MEMBERSHIP_ARC,
            element,
        )
        template.quintuple(
            previous_arc,
            sc_type.VAR_COMMON_ARC,
            ScAlias.MEMBERSHIP_ARC,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
        )
        return generate_by_template(template).get(ScAlias.MEMBERSHIP_ARC)

    @staticmethod
    def _mark_arc_with_rrel_last(last_arc: ScAddr) -> None:
        generate_connector(
            sc_type.CONST_PERM_POS_ARC,
            ScKeynodes[CommonIdentifiers.RREL_LAST],
            last_arc,
        )

    def _search_next_element_template(self, cur_element_arc: ScAddr) -> Optional[ScTemplateResult]:
        templ = ScTemplate()
        templ.quintuple(
            cur_element_arc,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_PERM_POS_ARC >> ScAlias.RELATION_ARC,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
        )
        templ.triple(self._set_node, ScAlias.RELATION_ARC, sc_type.UNKNOWN >> ScAlias.ELEMENT)
        search_results = search_by_template(templ)
        return search_results[0] if search_results else None
