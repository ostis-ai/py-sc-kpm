"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.client import check_elements, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScTemplate

from sc_kpm import ScKeynodes
from sc_kpm.sc_sets.sc_numbered_set import ScNumberedSet
from sc_kpm.utils.common_utils import generate_link, generate_node, generate_nodes
from tests.common_tests import BaseTestCase


class ScNumberedSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = generate_node(sc_type.CONST_NODE)
        element1 = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
        ScNumberedSet(element1, element2, set_node=set_node)
        self._assert_two_elements_num_set_template(set_node, element1, element2)

    def test_create_without_set_node(self):
        element1 = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
        sc_set = ScNumberedSet(element1, element2)
        self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    def test_create_with_set_type(self):
        element1 = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
        sc_set = ScNumberedSet(element1, element2, set_node_type=sc_type.CONST_NODE_STRUCTURE)
        self.assertEqual(check_elements(sc_set.set_node)[0], sc_type.CONST_NODE_STRUCTURE)
        self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    def test_create_large(self):
        elements = generate_nodes(*[sc_type.CONST_NODE] * 3)
        sc_set = ScNumberedSet(*elements)
        self.assertEqual(sc_set.elements_list, elements)

    def test_create_copy_num_set_node(self):
        element1 = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
        sc_set = ScNumberedSet(element1, element2)
        sc_set_copy = ScNumberedSet(set_node=sc_set.set_node)
        self._assert_two_elements_num_set_template(sc_set_copy.set_node, element1, element2)

    def test_add(self):
        element1 = generate_node(sc_type.CONST_NODE)
        sc_set = ScNumberedSet(element1)
        element2 = generate_node(sc_type.CONST_NODE)
        sc_set.add(element2)
        self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    def test_iterate(self):
        set_node = generate_node(sc_type.CONST_NODE)
        elements = [
            generate_node(sc_type.CONST_NODE),
            generate_link("abc"),
            generate_node(sc_type.CONST_NODE),
        ]
        sc_set = ScNumberedSet(*elements, set_node=set_node)
        for element_set, element_input in zip(sc_set, elements):
            self.assertEqual(element_set, element_input)

    def test_get_elements(self):
        set_node = generate_node(sc_type.CONST_NODE)
        elements = [
            generate_node(sc_type.CONST_NODE),
            generate_link("abc"),
            generate_node(sc_type.CONST_NODE),
        ]
        sc_set = ScNumberedSet(*elements, set_node=set_node)
        self.assertEqual(sc_set.elements_list, elements)

    def test_get_elements_empty(self):
        sc_set = ScNumberedSet()
        self.assertEqual(sc_set.elements_list, [])

    def test_get_power(self):
        set_node = generate_node(sc_type.CONST_NODE)
        elements = [
            generate_node(sc_type.CONST_NODE),
            generate_link("abc"),
            generate_node(sc_type.CONST_NODE),
        ]
        sc_set = ScNumberedSet(*elements, set_node=set_node)
        self.assertEqual(len(sc_set), len(elements))
        self.assertTrue(sc_set)

    def test_get_power_empty(self):
        sc_set = ScNumberedSet()
        self.assertEqual(len(sc_set), 0)
        self.assertFalse(sc_set)

    def test_get_by_index(self):
        element0 = generate_node(sc_type.CONST_NODE)
        element1 = generate_node(sc_type.CONST_NODE)
        sc_set = ScNumberedSet(element0, element1)
        self.assertEqual(sc_set[0], element0)
        self.assertEqual(sc_set[1], element1)
        self.assertRaises(KeyError, sc_set.__getitem__, 2)

    def test_contain(self):
        element_in = generate_node(sc_type.CONST_NODE)
        element_not_in = generate_node(sc_type.CONST_NODE)
        sc_set = ScNumberedSet(element_in)
        self.assertIn(element_in, sc_set)
        self.assertNotIn(element_not_in, sc_set)

    def test_remove(self):
        element1 = generate_node(sc_type.CONST_NODE)
        element_to_remove = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
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
        template.quintuple(
            set_node,
            sc_type.VAR_PERM_POS_ARC,
            element1,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.rrel_index(1),
        )
        template.quintuple(
            set_node,
            sc_type.VAR_PERM_POS_ARC,
            element2,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.rrel_index(2),
        )
        results = search_by_template(template)
        self.assertEqual(len(results), 1)
