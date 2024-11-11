"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.client import erase_elements, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScTemplate

from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_sets.sc_oriented_set import ScOrientedSet
from sc_kpm.utils.common_utils import generate_link, generate_node
from tests.common_tests import BaseTestCase


class ScOrientedSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = generate_node(sc_type.CONST_NODE)
        start_element = generate_node(sc_type.CONST_NODE)
        other_element = generate_node(sc_type.CONST_NODE)
        ScOrientedSet(start_element, other_element, set_node=set_node)
        self._assert_two_elements_oriented_set_template(set_node, start_element, other_element)

    def test_create_without_set_node(self):
        start_element = generate_node(sc_type.CONST_NODE)
        other_element = generate_node(sc_type.CONST_NODE)
        oriented_set = ScOrientedSet(start_element, other_element)
        self._assert_two_elements_oriented_set_template(oriented_set.set_node, start_element, other_element)

    def test_add_to_oriented_set(self):
        start_element = generate_node(sc_type.CONST_NODE)
        oriented_set = ScOrientedSet(start_element)
        other_element = generate_node(sc_type.CONST_NODE)
        oriented_set.add(other_element)
        self._assert_two_elements_oriented_set_template(oriented_set.set_node, start_element, other_element)

    def test_add_without_rrel_last(self):
        element1 = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
        element3 = generate_node(sc_type.CONST_NODE)
        oriented_set = ScOrientedSet(element1, element2)
        template = ScTemplate()
        template.quintuple(
            oriented_set.set_node,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.UNKNOWN,
            sc_type.VAR_PERM_POS_ARC >> ScAlias.RELATION_ARC,
            ScKeynodes[CommonIdentifiers.RREL_LAST],
        )
        rrel_last_connector = search_by_template(template)[0].get(ScAlias.RELATION_ARC)
        erase_elements(rrel_last_connector)
        oriented_set_continue = ScOrientedSet(set_node=oriented_set.set_node)
        oriented_set_continue.add(element3)
        self.assertEqual(len(oriented_set_continue), 3)

    def test_iterate(self):
        set_node = generate_node(sc_type.CONST_NODE)
        elements = [
            generate_node(sc_type.CONST_NODE),
            generate_link("abc"),
            generate_node(sc_type.CONST_NODE),
        ]
        sc_set = ScOrientedSet(*elements, set_node=set_node)
        for element_set, element_input in zip(sc_set, elements):
            self.assertEqual(element_set, element_input)

    def test_get_oriented_set_elements(self):
        set_node = generate_node(sc_type.CONST_NODE)
        elements = [
            generate_node(sc_type.CONST_NODE),
            generate_link("abc"),
            generate_node(sc_type.CONST_NODE),
        ]
        oriented_set = ScOrientedSet(*elements, set_node=set_node)
        self.assertEqual(oriented_set.elements_list, elements)

    def test_get_power(self):
        set_node = generate_node(sc_type.CONST_NODE)
        elements = [
            generate_node(sc_type.CONST_NODE),
            generate_link("abc"),
            generate_node(sc_type.CONST_NODE),
        ]
        sc_set = ScOrientedSet(*elements, set_node=set_node)
        self.assertEqual(len(sc_set), len(elements))

    def test_get_power_one(self):
        sc_set = ScOrientedSet(generate_node(sc_type.CONST_NODE))
        self.assertEqual(len(sc_set), 1)
        self.assertTrue(sc_set)

    def test_get_power_empty(self):
        sc_set = ScOrientedSet()
        self.assertEqual(len(sc_set), 0)
        self.assertFalse(sc_set)

    def test_contain(self):
        element_in = generate_node(sc_type.CONST_NODE)
        element_not_in = generate_node(sc_type.CONST_NODE)
        sc_set = ScOrientedSet(element_in)
        self.assertIn(element_in, sc_set)
        self.assertNotIn(element_not_in, sc_set)

    def test_remove(self):
        element1 = generate_node(sc_type.CONST_NODE)
        element_to_remove = generate_node(sc_type.CONST_NODE)
        element2 = generate_node(sc_type.CONST_NODE)
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
        connector1, connector2 = "connector1", "connector2"
        template = ScTemplate()
        template.quintuple(
            set_node,
            sc_type.VAR_PERM_POS_ARC >> connector1,
            start_element,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.rrel_index(1),
        )
        template.triple(
            set_node,
            sc_type.VAR_PERM_POS_ARC >> connector2,
            other_element,
        )
        template.quintuple(
            connector1,
            sc_type.VAR_COMMON_ARC,
            connector2,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
        )
        results = search_by_template(template)
        self.assertEqual(len(results), 1)
