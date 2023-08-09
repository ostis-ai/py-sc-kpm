"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client import ScAddr, ScTemplate, sc_types
from sc_client.init import sc_client, sc_keynodes
from sc_kpm.sc_sets.sc_numbered_set import ScNumberedSet
from sc_kpm.utils.common_utils import create_link, create_node, create_nodes
from tests.common_tests import BaseTestCase


class ScNumberedSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = create_node(sc_types.NODE_CONST)
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        ScNumberedSet(element1, element2, set_node=set_node)
        self._assert_two_elements_num_set_template(set_node, element1, element2)

    def test_create_without_set_node(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element1, element2)
        self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    def test_create_with_set_type(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element1, element2, set_node_type=sc_types.NODE_CONST_STRUCT)
        self.assertEqual(sc_client.check_elements(sc_set.set_node)[0], sc_types.NODE_CONST_STRUCT)
        self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    def test_create_large(self):
        elements = create_nodes(*[sc_types.NODE_CONST] * 3)
        sc_set = ScNumberedSet(*elements)
        self.assertEqual(sc_set.elements_list, elements)

    def test_create_copy_num_set_node(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element1, element2)
        sc_set_copy = ScNumberedSet(set_node=sc_set.set_node)
        self._assert_two_elements_num_set_template(sc_set_copy.set_node, element1, element2)

    def test_add(self):
        element1 = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element1)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set.add(element2)
        self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    def test_iterate(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScNumberedSet(*elements, set_node=set_node)
        for element_set, element_input in zip(sc_set, elements):
            self.assertEqual(element_set, element_input)

    def test_get_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScNumberedSet(*elements, set_node=set_node)
        self.assertEqual(sc_set.elements_list, elements)

    def test_get_elements_empty(self):
        sc_set = ScNumberedSet()
        self.assertEqual(sc_set.elements_list, [])

    def test_get_power(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScNumberedSet(*elements, set_node=set_node)
        self.assertEqual(len(sc_set), len(elements))
        self.assertTrue(sc_set)

    def test_get_power_empty(self):
        sc_set = ScNumberedSet()
        self.assertEqual(len(sc_set), 0)
        self.assertFalse(sc_set)

    def test_get_by_index(self):
        element0 = create_node(sc_types.NODE_CONST)
        element1 = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element0, element1)
        self.assertEqual(sc_set[0], element0)
        self.assertEqual(sc_set[1], element1)
        self.assertRaises(KeyError, sc_set.__getitem__, 2)

    def test_contain(self):
        element_in = create_node(sc_types.NODE_CONST)
        element_not_in = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element_in)
        self.assertIn(element_in, sc_set)
        self.assertNotIn(element_not_in, sc_set)

    def test_remove(self):
        element1 = create_node(sc_types.NODE_CONST)
        element_to_remove = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScNumberedSet(element1, element_to_remove, element2)
        self.assertEqual(len(sc_set), 3)
        sc_set.remove(element_to_remove)
        self.assertEqual(len(sc_set), 2)
        self.assertEqual(sc_set.elements_list, [element1, element2])
        sc_set.clear()
        self.assertTrue(sc_set.is_empty())
        self.assertEqual(sc_set.elements_list, [])

    def _assert_two_elements_num_set_template(self, set_node: ScAddr, element1: ScAddr, element2: ScAddr) -> None:
        template = ScTemplate()
        template.triple_with_relation(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            element1,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_keynodes.rrel_index(1),
        )
        template.triple_with_relation(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            element2,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_keynodes.rrel_index(2),
        )
        results = sc_client.template_search(template)
        self.assertEqual(len(results), 1)
