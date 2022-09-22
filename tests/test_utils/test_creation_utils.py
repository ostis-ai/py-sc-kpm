"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client import client
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate

from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.utils.common_utils import create_node
from sc_kpm.utils.creation_utils import (
    create_oriented_set,
    create_set,
    create_structure,
    wrap_in_oriented_set,
    wrap_in_set,
)
from tests.common_tests import BaseTestCase


class TestGenerationUtils(BaseTestCase):
    def test_wrap_in_oriented_set(self):
        set_node = create_node(sc_types.NODE_CONST)
        start_element = create_node(sc_types.NODE_CONST)
        other_element = create_node(sc_types.NODE_CONST)
        wrap_in_oriented_set(set_node, start_element, other_element)
        template = _get_oriented_set_template(set_node, start_element, other_element)
        assert client.template_search(template)

    def test_create_oriented_set(self):
        start_element = create_node(sc_types.NODE_CONST)
        other_element = create_node(sc_types.NODE_CONST)
        set_node = create_oriented_set(start_element, other_element)
        template = _get_oriented_set_template(set_node, start_element, other_element)
        assert client.template_search(template)

    def test_wrap_in_set(self):
        set_node = create_node(sc_types.NODE_CONST)
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        wrap_in_set(set_node, element1, element2)
        template = _get_set_template(set_node, element1, element2)
        assert client.template_search(template)

    def test_create_set(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        set_node = create_set(sc_types.NODE_CONST, element1, element2)
        template = _get_set_template(set_node, element1, element2)
        assert client.template_search(template)

    def test_create_structure(self):
        element1 = create_node(sc_types.NODE_CONST)
        element2 = create_node(sc_types.NODE_CONST)
        set_node = create_structure(element1, element2)
        template = _get_set_template(set_node, element1, element2)
        search_results = client.template_search(template)
        assert search_results
        assert search_results[0].addrs[0].value == set_node.value


def _get_oriented_set_template(set_node: ScAddr, start_element: ScAddr, other_element: ScAddr) -> ScTemplate:
    keynodes = ScKeynodes()
    rrel_one = keynodes[CommonIdentifiers.RREL_ONE]
    nrel_sequence = keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE]

    template = ScTemplate()
    template.triple_with_relation(
        set_node,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, edge1 := "edge1"],
        start_element,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        rrel_one,
    )
    template.triple(
        set_node,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, edge2 := "edge2"],
        other_element,
    )
    template.triple_with_relation(
        edge1,
        sc_types.EDGE_D_COMMON_VAR,
        edge2,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        nrel_sequence,
    )
    return template


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
    template = ScTemplate()
    template.triple(
        [sc_types.NODE_VAR_STRUCT, set_node := "_set_node"],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        element1,
    )
    template.triple(
        set_node,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        element2,
    )
    return template
