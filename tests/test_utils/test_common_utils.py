"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client import client
from sc_client.constants import sc_types

from sc_kpm.utils.common_utils import (
    check_edge,
    delete_edge,
    delete_elements,
    generate_binary_relation,
    generate_edge,
    generate_link,
    generate_links,
    generate_node,
    generate_nodes,
    generate_norole_relation,
    generate_role_relation,
    get_edge,
    get_edges,
    get_element_by_role_relation,
    get_link_content,
    get_system_idtf,
)
from tests.common_tests import BaseTestCase


class TestActionUtils(BaseTestCase):
    def test_node_utils(self):
        node = generate_node(sc_types.NODE_VAR_ROLE)
        node_2 = generate_node(sc_types.NODE_CONST_CLASS)
        assert node.is_valid() and node_2.is_valid()

        result = client.check_elements(node, node_2)
        assert len(result) == 2
        assert result[0].is_node() and result[0].is_var() and result[0].is_role()
        assert result[1].is_node() and result[1].is_const() and result[1].is_class()

        nodes_counter = 10
        node_list = generate_nodes(*[sc_types.NODE_CONST for _ in range(nodes_counter)])
        for node in node_list:
            assert node.is_valid()

        result = client.check_elements(*node_list)
        assert len(result) == nodes_counter
        for result_item in result:
            assert result_item.is_node() and result_item.is_const()

    def test_link_utils(self):
        link_content = "my link content"
        link = generate_link(link_content)
        assert link.is_valid()
        assert get_link_content(link) == link_content

        link_counter = 10
        link_list = generate_links(*[link_content for _ in range(link_counter)])
        assert len(link_list) == link_counter
        for link in link_list:
            assert link.is_valid()

        result = client.check_elements(*link_list)
        for result_item in result:
            assert result_item.is_valid() and result_item.is_link()

    def test_edge_utils(self):
        source, target = generate_nodes(sc_types.NODE_CONST_CLASS, sc_types.NODE_CONST)
        empty = get_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, source, target)
        assert empty.is_valid() is False

        edge = generate_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, source, target)
        assert edge.is_valid()
        same_edge = get_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, source, target)
        assert same_edge.is_valid() and same_edge.value == edge.value
        assert check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, source, target)

        edge_counter = 10
        for _ in range(edge_counter):
            generate_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, source, target)
        result = get_edges(sc_types.EDGE_ACCESS_VAR_POS_PERM, source, target)
        assert len(result) == edge_counter + 1
        for edge in result:
            assert edge.is_valid()

    def test_relation_utils(self):
        rrel_idtf = "rrel_test"
        nrel_idtf = "nrel_test"
        src, rrel_trg, nrel_trg = generate_nodes(sc_types.NODE_CONST, sc_types.NODE_CONST, sc_types.NODE_CONST)
        rrel_node = generate_node(sc_types.NODE_CONST_ROLE, rrel_idtf)
        nrel_node = generate_node(sc_types.NODE_CONST_ROLE, nrel_idtf)

        rrel_edge_1 = generate_binary_relation(sc_types.EDGE_ACCESS_CONST_POS_PERM, src, rrel_trg, rrel_node)
        rrel_edge_2 = generate_role_relation(src, rrel_trg, rrel_node)
        nrel_edge_1 = generate_binary_relation(sc_types.EDGE_D_COMMON_CONST, src, nrel_trg, nrel_node)
        nrel_edge_2 = generate_norole_relation(src, nrel_trg, nrel_node)
        edges = [rrel_edge_1, rrel_edge_2, nrel_edge_1, nrel_edge_2]
        for edge in edges:
            assert edge.is_valid()

        result = client.check_elements(*edges)
        for result_item in result:
            assert result_item.is_valid() and result_item.is_edge() and result_item.is_const()
        assert result[0].is_pos() and result[1].is_pos()
        assert result[2].is_pos() is False and result[3].is_pos() is False

        expected_rrel_target = get_element_by_role_relation(src, rrel_node)
        expected_empty = get_element_by_role_relation(src, nrel_node)
        assert expected_rrel_target.is_valid()
        assert expected_rrel_target.value == rrel_trg.value
        assert expected_empty.is_valid() is False

    def test_get_system_idtf(self):
        test_idtf = "test_identifier"
        test_node = generate_node(sc_types.NODE_CONST_ROLE, test_idtf)
        assert get_system_idtf(test_node) == test_idtf

    def test_deletion_utils(self):
        src, rrel_trg, nrel_trg = generate_nodes(sc_types.NODE_CONST, sc_types.NODE_CONST, sc_types.NODE_CONST)
        rrel_edge = generate_binary_relation(sc_types.EDGE_ACCESS_CONST_POS_PERM, src, rrel_trg)
        nrel_edge = generate_norole_relation(src, nrel_trg)
        assert delete_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, src, rrel_trg)
        assert delete_elements(nrel_edge, src, rrel_trg, nrel_trg)

        result = client.check_elements(rrel_edge)[0]
        assert result.is_valid() is False
