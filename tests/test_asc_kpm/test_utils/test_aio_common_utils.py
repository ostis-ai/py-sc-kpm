"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.asc_keynodes_ import asc_keynodes
from asc_kpm.utils.aio_common_utils import (
    check_edge,
    create_binary_relation,
    create_edge,
    create_edges,
    create_link,
    create_links,
    create_node,
    create_nodes,
    create_norole_relation,
    create_role_relation,
    delete_edges,
    get_edge,
    get_edges,
    get_element_by_norole_relation,
    get_element_by_role_relation,
    get_link_content_data,
    get_system_idtf,
)


class TestActionUtils(AsyncioScKpmTestCase):
    async def test_node_utils(self):
        node = await create_node(sc_types.NODE_VAR_ROLE)
        node_2 = await create_node(sc_types.NODE_CONST_CLASS)
        assert node.is_valid() and node_2.is_valid()

        result = await asc_client.check_elements(node, node_2)
        assert len(result) == 2
        assert result[0].is_node() and result[0].is_var() and result[0].is_role()
        assert result[1].is_node() and result[1].is_const() and result[1].is_class()

        nodes_counter = 10
        node_list = await create_nodes(*[sc_types.NODE_CONST for _ in range(nodes_counter)])
        for node in node_list:
            assert node.is_valid()

        result = await asc_client.check_elements(*node_list)
        assert len(result) == nodes_counter
        for result_item in result:
            assert result_item.is_node() and result_item.is_const()

    async def test_link_utils(self):
        link_content = "my link content"
        link = await create_link(link_content)
        assert link.is_valid()
        assert await get_link_content_data(link) == link_content

        link_counter = 10
        link_list = await create_links(*[link_content for _ in range(link_counter)])
        assert len(link_list) == link_counter
        for link in link_list:
            assert link.is_valid()

        result = await asc_client.check_elements(*link_list)
        for result_item in result:
            assert result_item.is_valid() and result_item.is_link()

    async def test_edge_utils(self):
        source, target = await create_nodes(sc_types.NODE_CONST_CLASS, sc_types.NODE_CONST)
        empty = await get_edge(source, target, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        assert empty.is_valid() is False

        edge = await create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, source, target)
        assert edge.is_valid()
        same_edge = await get_edge(source, target, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        assert same_edge.is_valid() and same_edge.value == edge.value
        assert await check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, source, target)

        source, target, target2 = await create_nodes(
            sc_types.NODE_CONST_CLASS, sc_types.NODE_CONST, sc_types.NODE_CONST
        )
        edges = await create_edges(sc_types.EDGE_ACCESS_CONST_POS_PERM, source, target, target2)
        assert all(edge_.is_valid() for edge_ in edges)
        same_target1 = await get_edge(source, target, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        same_target2 = await get_edge(source, target2, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        assert edges == [same_target1, same_target2]

        edge_counter = 10
        for _ in range(edge_counter):
            await create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, source, target)
        result = await get_edges(source, target, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        assert len(result) == edge_counter + 1
        for edge in result:
            assert edge.is_valid()

    async def test_relation_utils(self):
        src, rrel_trg, nrel_trg = await create_nodes(sc_types.NODE_CONST, sc_types.NODE_CONST, sc_types.NODE_CONST)
        rrel_node = await create_node(sc_types.NODE_CONST_ROLE)
        nrel_node = await create_node(sc_types.NODE_CONST_NOROLE)

        rrel_edge_1 = await create_binary_relation(sc_types.EDGE_ACCESS_CONST_POS_PERM, src, rrel_trg, rrel_node)
        rrel_edge_2 = await create_role_relation(src, rrel_trg, rrel_node)
        nrel_edge_1 = await create_binary_relation(sc_types.EDGE_D_COMMON_CONST, src, nrel_trg, nrel_node)
        nrel_edge_2 = await create_norole_relation(src, nrel_trg, nrel_node)
        edges = [rrel_edge_1, rrel_edge_2, nrel_edge_1, nrel_edge_2]
        for edge in edges:
            assert edge.is_valid()

        result = await asc_client.check_elements(*edges)
        for result_item in result:
            assert result_item.is_valid() and result_item.is_edge() and result_item.is_const()
        assert result[0].is_pos() and result[1].is_pos()
        assert result[2].is_pos() is False and result[3].is_pos() is False

        expected_rrel_target = await get_element_by_role_relation(src, rrel_node)
        expected_empty = await get_element_by_role_relation(src, nrel_node)
        assert expected_rrel_target.is_valid()
        assert expected_rrel_target.value == rrel_trg.value
        assert expected_empty.is_valid() is False

        expected_nrel_target = await get_element_by_norole_relation(src, nrel_node)
        expected_empty = await get_element_by_norole_relation(src, rrel_node)
        assert expected_nrel_target.is_valid()
        assert expected_nrel_target.value == nrel_trg.value
        assert expected_empty.is_valid() is False

    async def test_get_system_idtf(self):
        test_idtf = "rrel_1"
        test_node = await asc_keynodes.get_valid(test_idtf)
        assert await get_system_idtf(test_node) == test_idtf

    async def test_deletion_utils(self):
        src, rrel_trg, nrel_trg = await create_nodes(sc_types.NODE_CONST, sc_types.NODE_CONST, sc_types.NODE_CONST)
        rrel_edge = await create_binary_relation(sc_types.EDGE_ACCESS_CONST_POS_PERM, src, rrel_trg)
        nrel_edge = await create_norole_relation(src, nrel_trg)
        assert await delete_edges(src, rrel_trg, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        assert await asc_client.delete_elements(nrel_edge, src, rrel_trg, nrel_trg)

        result = (await asc_client.check_elements(rrel_edge))[0]
        assert result.is_valid() is False
