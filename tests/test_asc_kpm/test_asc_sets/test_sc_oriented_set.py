"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types
from sc_client.core.sc_client_instance import sc_client
from sc_client.models import ScAddr, ScTemplate
from test_sc_kpm.common_tests import BaseTestCase

from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_keynodes_ import sc_keynodes
from sc_kpm.sc_sets import ScOrientedSet
from sc_kpm.utils.common_utils import create_link, create_node


class ScOrientedSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = create_node(sc_types.NODE_CONST)
        start_element = create_node(sc_types.NODE_CONST)
        other_element = create_node(sc_types.NODE_CONST)
        ScOrientedSet(start_element, other_element, set_node=set_node)
        self._assert_two_elements_oriented_set_template(set_node, start_element, other_element)

    def test_create_without_set_node(self):
        start_element = create_node(sc_types.NODE_CONST)
        other_element = create_node(sc_types.NODE_CONST)
        oriented_set = ScOrientedSet(start_element, other_element)
        self._assert_two_elements_oriented_set_template(oriented_set.set_node, start_element, other_element)

    def test_add_to_oriented_set(self):
        start_element = create_node(sc_types.NODE_CONST)
        oriented_set = ScOrientedSet(start_element)
        other_element = create_node(sc_types.NODE_CONST)
        oriented_set.add(other_element)
        self._assert_two_elements_oriented_set_template(oriented_set.set_node, start_element, other_element)

    def test_add_without_rrel_last(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        element3 = create_node(sc_types.NODE_CONST)
        oriented_set = ScOrientedSet(element1, element2)
        template = ScTemplate()
        template.triple_with_relation(
            oriented_set.set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.UNKNOWN,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.RELATION_EDGE,
            sc_keynodes[CommonIdentifiers.RREL_LAST],
        )
        rrel_last_edge = sc_client.template_search(template)[0].get(ScAlias.RELATION_EDGE)
        sc_client.delete_elements(rrel_last_edge)
        oriented_set_continue = ScOrientedSet(set_node=oriented_set.set_node)
        oriented_set_continue.add(element3)
        self.assertEqual(len(oriented_set_continue), 3)

    def test_iterate(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScOrientedSet(*elements, set_node=set_node)
        for element_set, element_input in zip(sc_set, elements):
            self.assertEqual(element_set, element_input)

    def test_get_oriented_set_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        oriented_set = ScOrientedSet(*elements, set_node=set_node)
        self.assertEqual(oriented_set.elements_list, elements)

    def test_get_power(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScOrientedSet(*elements, set_node=set_node)
        self.assertEqual(len(sc_set), len(elements))

    def test_get_power_one(self):
        sc_set = ScOrientedSet(create_node(sc_types.NODE_CONST))
        self.assertEqual(len(sc_set), 1)
        self.assertTrue(sc_set)

    def test_get_power_empty(self):
        sc_set = ScOrientedSet()
        self.assertEqual(len(sc_set), 0)
        self.assertFalse(sc_set)

    def test_contain(self):
        element_in = create_node(sc_types.NODE_CONST)
        element_not_in = create_node(sc_types.NODE_CONST)
        sc_set = ScOrientedSet(element_in)
        self.assertIn(element_in, sc_set)
        self.assertNotIn(element_not_in, sc_set)

    def test_remove(self):
        element1 = create_node(sc_types.NODE_CONST)
        element_to_remove = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScOrientedSet(element1, element_to_remove, element2)
        self.assertEqual(len(sc_set), 3)
        sc_set.remove(element_to_remove)
        self.assertEqual(len(sc_set), 2)
        self.assertEqual(sc_set.elements_list, [element1, element2])
        sc_set.clear()
        self.assertTrue(sc_set.is_empty())
        self.assertEqual(sc_set.elements_list, [])

    def _assert_two_elements_oriented_set_template(
        self, set_node: ScAddr, start_element: ScAddr, other_element: ScAddr
    ) -> None:
        edge1, edge2 = "edge1", "edge2"
        template = ScTemplate()
        template.triple_with_relation(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> edge1,
            start_element,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_keynodes.rrel_index(1),
        )
        template.triple(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> edge2,
            other_element,
        )
        template.triple_with_relation(
            edge1,
            sc_types.EDGE_D_COMMON_VAR,
            edge2,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
        )
        results = sc_client.template_search(template)
        self.assertEqual(len(results), 1)
