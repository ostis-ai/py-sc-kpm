"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client import ScAddr, ScTemplate, sc_types
from sc_client.init import sc_client
from sc_kpm.sc_sets.sc_set import ScSet
from sc_kpm.utils.common_utils import create_node
from tests.common_tests import BaseTestCase


class ScSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = create_node(sc_types.NODE_CONST)
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        ScSet(element1, element2, set_node=set_node)
        self._assert_two_elements_set_template(set_node, element1, element2)

    def test_create_without_set_node(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1, element2)
        self.assertEqual(sc_client.check_elements(sc_set.set_node)[0], sc_types.NODE_CONST)
        self._assert_two_elements_set_template(sc_set.set_node, element1, element2)

    def test_create_with_set_type(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1, element2, set_node_type=sc_types.NODE_CONST_STRUCT)
        self.assertEqual(sc_client.check_elements(sc_set.set_node)[0], sc_types.NODE_CONST_STRUCT)
        self._assert_two_elements_set_template(sc_set.set_node, element1, element2)

    def test_create_copy_set_node(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1, element2)
        sc_set_copy = ScSet(set_node=sc_set.set_node)
        self.assertEqual(sc_set, sc_set_copy)
        self._assert_two_elements_set_template(sc_set_copy.set_node, element1, element2)

    def test_get_elements_set(self):
        elements = {create_node(sc_types.NODE_CONST), create_node(sc_types.NODE_CONST)}
        sc_set = ScSet(*elements)
        self.assertEqual(sc_set.elements_set, elements)

    def test_get_elements_set_empty(self):
        sc_set = ScSet()
        self.assertEqual(sc_set.elements_set, set())

    def test_iterate(self):
        elements = {create_node(sc_types.NODE_CONST), create_node(sc_types.NODE_CONST)}
        sc_set = ScSet(*elements)
        for set_element in sc_set:
            self.assertIn(set_element, elements)

    def test_add(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1)
        sc_set.add(element2)
        self.assertEqual(sc_client.check_elements(sc_set.set_node)[0], sc_types.NODE_CONST)
        self._assert_two_elements_set_template(sc_set.set_node, element1, element2)

    def test_add_element_twice(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        elements = {element1, element2}
        sc_set = ScSet(*elements)
        sc_set.add(element2)  # element is added second time
        self.assertEqual(sc_set.elements_set, elements)  # element1 will not duplicate

    def test_get_power(self):
        element = create_node(sc_types.NODE_CONST)
        sc_set = ScSet()
        self.assertEqual(len(sc_set), 0)
        sc_set.add(element)
        self.assertEqual(len(sc_set), 1)

    def test_booleans(self):
        """Test __bool__(), is_empty() and __contains__"""
        sc_set = ScSet()
        self.assertFalse(bool(sc_set))
        self.assertTrue(sc_set.is_empty())

        element = create_node(sc_types.NODE_CONST)
        sc_set.add(element)
        self.assertTrue(bool(sc_set))
        self.assertFalse(sc_set.is_empty())

        self.assertIn(element, sc_set)
        self.assertNotIn(ScAddr(0), sc_set)

    def test_remove(self):
        element = create_node(sc_types.NODE_CONST)
        element_to_remove = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element, element_to_remove)
        self.assertEqual(len(sc_set), 2)
        sc_set.remove(element_to_remove)
        self.assertEqual(len(sc_set), 1)
        self.assertEqual(sc_set.elements_set, {element})

    def test_clear(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1, element2)
        self.assertFalse(sc_set.is_empty())
        sc_set.clear()
        self.assertTrue(sc_set.is_empty())

    def _assert_two_elements_set_template(self, set_node: ScAddr, element1: ScAddr, element2: ScAddr) -> None:
        template = ScTemplate()
        template.triple(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            element1,
        )
        template.triple(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            element2,
        )
        results = sc_client.template_search(template)
        self.assertEqual(len(results), 1)
