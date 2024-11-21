from __future__ import annotations

from typing import Iterator

from sc_client.client import erase_elements, generate_elements, search_by_template
from sc_client.constants import ScType, sc_type
from sc_client.models import ScAddr, ScConstruction, ScTemplate, ScTemplateResult

from sc_kpm.utils.common_utils import generate_node


class ScSet:
    """
    ScSet is a class for handling set construction in kb.

    It has main set_node and elements.
    """

    def __init__(self, *elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None) -> None:
        """
        Initialize ScSet.

        Receive or generate set_node and add elements.

        :param elements: Elements of a set to initialize it.
        :param set_node: Set node has arcs to each element.
        Optional parameter: it will be generated if it doesn't exist.
        :param set_node_type: ScType for generated set node.
        """

        if set_node is None:
            if set_node_type is None:
                set_node_type = sc_type.CONST_NODE
            set_node = generate_node(set_node_type)
        self._set_node = set_node
        self.add(*elements)

    def add(self, *elements: ScAddr) -> None:
        """Add elements to ScSet"""
        if elements:
            construction = ScConstruction()
            for element in elements:
                construction.generate_connector(sc_type.CONST_PERM_POS_ARC, self._set_node, element)
            generate_elements(construction)

    @property
    def set_node(self) -> ScAddr:
        """Get the main element of ScSet"""
        return self._set_node

    def __eq__(self, other: ScSet) -> bool:
        return self._set_node == other._set_node

    @property
    def elements_set(self) -> set[ScAddr]:
        """Set of elements without order and duplicates"""
        search_results = self._elements_search_results()
        elements = {result[2] for result in search_results}
        return elements

    def __len__(self) -> int:
        """Get ScSet power"""
        return len(self.elements_set)  # No duplicates

    def __bool__(self) -> bool:
        """Check ScSet is not empty"""
        return bool(self._elements_search_results())

    def is_empty(self) -> bool:
        """Check if ScSet doesn't contain any element"""
        return not bool(self)

    def __iter__(self) -> Iterator[ScAddr]:
        """Iterate by ScSet elements"""
        return iter(self.elements_set)

    def __contains__(self, element: ScAddr) -> bool:
        """Check if ScSet contains element"""
        return element in self.elements_set

    def remove(self, *elements: ScAddr) -> None:
        """Erase the connections between set_node and elements"""
        templ = ScTemplate()
        for element in elements:
            templ.triple(self._set_node, sc_type.VAR_PERM_POS_ARC, element)
        template_results = search_by_template(templ)
        erase_elements(*(res[1] for res in template_results))

    def clear(self) -> None:
        """Erase the arcs between set_node and all elements"""
        template_results = self._elements_search_results()
        erase_elements(*(res[1] for res in template_results))

    def _elements_search_results(self) -> list[ScTemplateResult]:
        """Template search of all elements"""
        templ = ScTemplate()
        templ.triple(self._set_node, sc_type.VAR_PERM_POS_ARC, sc_type.UNKNOWN)
        return search_by_template(templ)
