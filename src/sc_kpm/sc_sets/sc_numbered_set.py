from typing import Iterator, List

from sc_client.client import generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScTemplate

from sc_kpm.sc_keynodes import ScKeynodes
from sc_kpm.sc_sets.sc_set import ScSet


class ScNumberedSet(ScSet):
    """
    ScNumberedSet is a class for handling numbered set structure in kb.

    It has main set_node and arc elements:
    Arcs to each element marked with 'rrel_1', 'rrel_2', and so on nodes.
    """

    def add(self, *elements: ScAddr) -> None:
        """Add elements to ScNumberedSet"""
        if elements:
            template = ScTemplate()
            for index, element in enumerate(elements, len(self) + 1):
                template.quintuple(
                    self._set_node,
                    sc_type.VAR_PERM_POS_ARC,
                    element,
                    sc_type.VAR_PERM_POS_ARC,
                    ScKeynodes.rrel_index(index),
                )
            generate_by_template(template)

    def __iter__(self) -> Iterator[ScAddr]:
        return iter(self.elements_list)

    @property
    def elements_list(self) -> List[ScAddr]:
        """Iterate by ScNumberedSet elements"""
        templ = ScTemplate()
        templ.quintuple(
            self._set_node,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.UNKNOWN,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE_ROLE,
        )
        results = search_by_template(templ)
        sorted_results = sorted((result for result in results), key=lambda res: res[4].value)
        # Sort rrel elements addrs
        return [result[2] for result in sorted_results]

    def __getitem__(self, i: int) -> ScAddr:
        templ = ScTemplate()
        templ.quintuple(
            self._set_node,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.UNKNOWN,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.rrel_index(i + 1),
        )
        results = search_by_template(templ)
        if not results:
            raise KeyError("No element by index")
        return results[0][2]

    def remove(self, *elements: ScAddr) -> None:
        """Clear and add existing elements without given ones"""
        # TODO: optimize
        elements_new = [element for element in self.elements_list if element not in elements]
        self.clear()
        self.add(*elements_new)
