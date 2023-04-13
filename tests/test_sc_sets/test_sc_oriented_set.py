"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.client import template_search
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate

from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.sc_sets.sc_oriented_set import ScOrientedSet
from sc_kpm.utils.common_utils import create_link, create_node
from tests.common_tests import BaseTestCase


class ScOrientedSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = create_node(sc_types.NODE_CONST)
        start_element = create_node(sc_types.NODE_CONST)
        other_element = create_node(sc_types.NODE_CONST)
        ScOrientedSet(start_element, other_element, set_node=set_node)
        template = _get_oriented_set_template(set_node, start_element, other_element)
        self.assertTrue(template_search(template))

    def test_create_without_set_node(self):
        start_element = create_node(sc_types.NODE_CONST)
        other_element = create_node(sc_types.NODE_CONST)
        oriented_set = ScOrientedSet(start_element, other_element)
        template = _get_oriented_set_template(oriented_set.set_node, start_element, other_element)
        self.assertTrue(template_search(template))

    def test_add_to_oriented_set(self):
        start_element = create_node(sc_types.NODE_CONST)
        oriented_set = ScOrientedSet(start_element)
        other_element = create_node(sc_types.NODE_CONST)
        oriented_set.add(other_element)
        template = _get_oriented_set_template(oriented_set.set_node, start_element, other_element)
        self.assertTrue(template_search(template))

    def test_get_oriented_set_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        oriented_set = ScOrientedSet(*elements, set_node=set_node)
        self.assertEqual(oriented_set.elements, elements)

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


def _get_oriented_set_template(set_node: ScAddr, start_element: ScAddr, other_element: ScAddr) -> ScTemplate:
    edge1, edge2 = "edge1", "edge2"
    template = ScTemplate()
    template.triple_with_relation(
        set_node,
        sc_types.EDGE_ACCESS_VAR_POS_PERM >> edge1,
        start_element,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes.rrel(1),
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
        ScKeynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE],
    )
    return template
