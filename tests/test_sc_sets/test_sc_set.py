"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.client import template_search
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate

from sc_kpm.sc_sets.sc_set import ScSet
from sc_kpm.utils.common_utils import create_link, create_node
from tests.common_tests import BaseTestCase


class ScSetTestCase(BaseTestCase):
    def test_create_with_set_node(self):
        set_node = create_node(sc_types.NODE_CONST)
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        ScSet(element1, element2, set_node=set_node)
        template = _get_set_template(set_node, element1, element2)
        self.assertTrue(template_search(template))

    def test_create_without_set_node(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1, element2)
        template = _get_set_template(sc_set.set_node, element1, element2)
        self.assertTrue(template_search(template))

    def test_create_with_set_type(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1, element2, set_node_type=sc_types.NODE_CONST_STRUCT)
        template = _get_structure_template(element1, element2)
        search_results = template_search(template)
        self.assertTrue(search_results)
        self.assertEqual(search_results[0][0], sc_set.set_node)

    def test_add(self):
        element1 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set.add(element2)
        template = _get_set_template(sc_set.set_node, element1, element2)
        self.assertTrue(template_search(template))

    def test_update(self):
        element1 = create_node(sc_types.NODE_CONST)
        sc_set = ScSet(element1)
        element2 = create_node(sc_types.NODE_CONST)
        sc_set.add(element1, element2)
        template = _get_set_template(sc_set.set_node, element1, element2)
        self.assertTrue(template_search(template))

    def test_get_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScSet(*elements, set_node=set_node)
        self.assertEqual(sc_set.elements, elements)

    def test_get_elements_empty(self):
        sc_set = ScSet()
        self.assertEqual(sc_set.elements, [])

    def test_get_power(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        sc_set = ScSet(*elements, set_node=set_node)
        self.assertEqual(len(sc_set), len(elements))

    def test_get_power_empty(self):
        sc_set = ScSet()
        self.assertEqual(len(sc_set), 0)


def _get_set_template(set_node: ScAddr, element1: ScAddr, element2: ScAddr) -> ScTemplate:
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
    return template


def _get_structure_template(element1: ScAddr, element2: ScAddr) -> ScTemplate:
    structure_node = "_structure_node"
    template = ScTemplate()
    template.triple(
        sc_types.NODE_VAR_STRUCT >> structure_node,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        element1,
    )
    template.triple(
        structure_node,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        element2,
    )
    return template
