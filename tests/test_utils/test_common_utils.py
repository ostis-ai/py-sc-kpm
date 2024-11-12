"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client import client
from sc_client.client import erase_elements
from sc_client.constants import sc_type

from sc_kpm import ScKeynodes
from sc_kpm.utils.common_utils import (
    check_connector,
    generate_binary_relation,
    generate_connector,
    generate_connectors,
    generate_link,
    generate_links,
    generate_node,
    generate_nodes,
    generate_non_role_relation,
    generate_role_relation,
    erase_connectors,
    get_connector,
    get_connectors,
    search_element_by_non_role_relation,
    get_element_by_role_relation,
    get_link_content_data,
    get_element_system_identifier,
)
from tests.common_tests import BaseTestCase


class TestActionUtils(BaseTestCase):
    def test_node_utils(self):
        node = generate_node(sc_type.NODE_VAR_ROLE)
        node_2 = generate_node(sc_type.CONST_NODE_CLASS)
        assert node.is_valid() and node_2.is_valid()

        result = client.check_elements(node, node_2)
        assert len(result) == 2
        assert result[0].is_node() and result[0].is_var() and result[0].is_role()
        assert result[1].is_node() and result[1].is_const() and result[1].is_class()

        nodes_counter = 10
        node_list = generate_nodes(*[sc_type.CONST_NODE for _ in range(nodes_counter)])
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
        assert get_link_content_data(link) == link_content

        link_counter = 10
        link_list = generate_links(*[link_content for _ in range(link_counter)])
        assert len(link_list) == link_counter
        for link in link_list:
            assert link.is_valid()

        result = client.check_elements(*link_list)
        for result_item in result:
            assert result_item.is_valid() and result_item.is_link()

    def test_connector_utils(self):
        source, target = generate_nodes(sc_type.CONST_NODE_CLASS, sc_type.CONST_NODE)
        empty = get_connector(source, target, sc_type.VAR_PERM_POS_ARC)
        assert empty.is_valid() is False

        connector = generate_connector(sc_type.CONST_PERM_POS_ARC, source, target)
        assert connector.is_valid()
        same_connector = get_connector(source, target, sc_type.VAR_PERM_POS_ARC)
        assert same_connector.is_valid() and same_connector.value == connector.value
        assert check_connector(sc_type.VAR_PERM_POS_ARC, source, target)

        source, target, target2 = generate_nodes(sc_type.CONST_NODE_CLASS, sc_type.CONST_NODE, sc_type.CONST_NODE)
        connectors = generate_connectors(sc_type.CONST_PERM_POS_ARC, source, target, target2)
        assert all(connector_.is_valid() for connector_ in connectors)
        same_target1 = get_connector(source, target, sc_type.VAR_PERM_POS_ARC)
        same_target2 = get_connector(source, target2, sc_type.VAR_PERM_POS_ARC)
        assert connectors == [same_target1, same_target2]

        connector_counter = 10
        for _ in range(connector_counter):
            generate_connector(sc_type.CONST_PERM_POS_ARC, source, target)
        result = get_connectors(source, target, sc_type.VAR_PERM_POS_ARC)
        assert len(result) == connector_counter + 1
        for connector in result:
            assert connector.is_valid()

    def test_relation_utils(self):
        src, rrel_trg, nrel_trg = generate_nodes(sc_type.CONST_NODE, sc_type.CONST_NODE, sc_type.CONST_NODE)
        rrel_node = generate_node(sc_type.CONST_NODE_ROLE)
        nrel_node = generate_node(sc_type.CONST_NODE_NON_ROLE)

        rrel_connector_1 = generate_binary_relation(sc_type.CONST_PERM_POS_ARC, src, rrel_trg, rrel_node)
        rrel_connector_2 = generate_role_relation(src, rrel_trg, rrel_node)
        nrel_connector_1 = generate_binary_relation(sc_type.CONST_COMMON_ARC, src, nrel_trg, nrel_node)
        nrel_connector_2 = generate_non_role_relation(src, nrel_trg, nrel_node)
        connectors = [rrel_connector_1, rrel_connector_2, nrel_connector_1, nrel_connector_2]
        for connector in connectors:
            assert connector.is_valid()

        result = client.check_elements(*connectors)
        for result_item in result:
            assert result_item.is_valid() and result_item.is_connector() and result_item.is_const()
        assert result[0].is_pos() and result[1].is_pos()
        assert result[2].is_pos() is False and result[3].is_pos() is False

        expected_rrel_target = get_element_by_role_relation(src, rrel_node)
        expected_empty = get_element_by_role_relation(src, nrel_node)
        assert expected_rrel_target.is_valid()
        assert expected_rrel_target.value == rrel_trg.value
        assert expected_empty.is_valid() is False

        expected_nrel_target = search_element_by_non_role_relation(src, nrel_node)
        expected_empty = search_element_by_non_role_relation(src, rrel_node)
        assert expected_nrel_target.is_valid()
        assert expected_nrel_target.value == nrel_trg.value
        assert expected_empty.is_valid() is False

    def test_get_element_system_identifier(self):
        test_idtf = "rrel_1"
        test_node = ScKeynodes[test_idtf]
        assert get_element_system_identifier(test_node) == test_idtf

    def test_deletion_utils(self):
        src, rrel_trg, nrel_trg = generate_nodes(sc_type.CONST_NODE, sc_type.CONST_NODE, sc_type.CONST_NODE)
        rrel_connector = generate_binary_relation(sc_type.CONST_PERM_POS_ARC, src, rrel_trg)
        nrel_connector = generate_non_role_relation(src, nrel_trg)
        assert erase_connectors(src, rrel_trg, sc_type.VAR_PERM_POS_ARC)
        assert erase_elements(nrel_connector, src, rrel_trg, nrel_trg)

        result = client.check_elements(rrel_connector)[0]
        assert result.is_valid() is False
