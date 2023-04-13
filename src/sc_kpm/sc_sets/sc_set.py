from typing import Iterator, List

from sc_client.client import create_elements
from sc_client.constants import ScType, sc_types
from sc_client.models import ScAddr, ScConstruction

from sc_kpm.sc_sets.sc_set_abstract import ScSetAbstract


class ScSet(ScSetAbstract):
    def __init__(self, *elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None) -> None:
        if set_node is not None:
            super().__init__(set_node)
            self.add(*elements)
        else:
            construction = ScConstruction()
            set_node_alias = "_set_node"
            if set_node_type is None:
                set_node_type = sc_types.NODE_CONST
            construction.create_node(set_node_type, set_node_alias)
            for element in elements:
                construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, set_node_alias, element)
            set_node = create_elements(construction)[0]
            super().__init__(set_node)

    def add(self, *elements: ScAddr) -> None:
        if elements:
            construction = ScConstruction()
            for element in elements:
                construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, self._set_node, element)
            create_elements(construction)

    def update(self, *elements: ScAddr) -> None:
        """Add elements to set if it doesn't contain them"""
        if elements:
            set_elements = self.elements
            construction = ScConstruction()
            for element in elements:
                if element not in set_elements:
                    construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, self._set_node, element)
            if construction.commands:
                create_elements(construction)

    def __iter__(self) -> Iterator[ScAddr]:
        """Iterate by elements of set"""
        search_results = self._elements_search_results()
        for result in reversed(search_results):  # Elements are found in reverse order
            yield result[2]

    @property
    def elements(self) -> List[ScAddr]:
        return list(self)
