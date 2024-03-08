"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScTemplate
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.asc_keynodes_ import asc_keynodes
from asc_kpm.asc_sets import AScOrientedSet
from asc_kpm.utils import create_link, create_node
from sc_kpm.identifiers import CommonIdentifiers, ScAlias


class AScOrientedSetTestCase(AsyncioScKpmTestCase):
    async def test_create_with_set_node(self):
        set_node = await create_node(sc_types.NODE_CONST)
        start_element = await create_node(sc_types.NODE_CONST)
        other_element = await create_node(sc_types.NODE_CONST)
        await AScOrientedSet.create(start_element, other_element, set_node=set_node)
        await self._assert_two_elements_oriented_set_template(set_node, start_element, other_element)

    async def test_create_without_set_node(self):
        start_element = await create_node(sc_types.NODE_CONST)
        other_element = await create_node(sc_types.NODE_CONST)
        oriented_set = await AScOrientedSet.create(start_element, other_element)
        await self._assert_two_elements_oriented_set_template(oriented_set.set_node, start_element, other_element)

    async def test_add_to_oriented_set(self):
        start_element = await create_node(sc_types.NODE_CONST)
        oriented_set = await AScOrientedSet.create(start_element)
        other_element = await create_node(sc_types.NODE_CONST)
        await oriented_set.add(other_element)
        await self._assert_two_elements_oriented_set_template(oriented_set.set_node, start_element, other_element)

    async def test_add_without_rrel_last(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        element3 = await create_node(sc_types.NODE_CONST)
        oriented_set = await AScOrientedSet.create(element1, element2)
        template = ScTemplate()
        template.triple_with_relation(
            oriented_set.set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.UNKNOWN,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> ScAlias.RELATION_EDGE,
            await asc_keynodes.get_valid(CommonIdentifiers.RREL_LAST),
        )
        rrel_last_edge = (await asc_client.template_search(template))[0].get(ScAlias.RELATION_EDGE)
        await asc_client.delete_elements(rrel_last_edge)
        oriented_set_copy = await AScOrientedSet.create(set_node=oriented_set.set_node)
        await oriented_set_copy.add(element3)
        self.assertEqual(await oriented_set_copy.len(), 3)

    async def test_iterate(self):
        set_node = await create_node(sc_types.NODE_CONST)
        elements = [
            await create_node(sc_types.NODE_CONST),
            await create_link("abc"),
            await create_node(sc_types.NODE_CONST),
        ]
        sc_set = await AScOrientedSet.create(*elements, set_node=set_node)
        self.assertEqual([element async for element in sc_set], elements)

    async def test_get_oriented_set_elements(self):
        set_node = await create_node(sc_types.NODE_CONST)
        elements = [
            await create_node(sc_types.NODE_CONST),
            await create_link("abc"),
            await create_node(sc_types.NODE_CONST),
        ]
        oriented_set = await AScOrientedSet.create(*elements, set_node=set_node)
        self.assertEqual(await oriented_set.elements_list, elements)

    async def test_get_power(self):
        set_node = await create_node(sc_types.NODE_CONST)
        elements = [
            await create_node(sc_types.NODE_CONST),
            await create_link("abc"),
            await create_node(sc_types.NODE_CONST),
        ]
        sc_set = await AScOrientedSet.create(*elements, set_node=set_node)
        self.assertEqual(await sc_set.len(), len(elements))

    async def test_get_power_one(self):
        sc_set = await AScOrientedSet.create(await create_node(sc_types.NODE_CONST))
        self.assertEqual(await sc_set.len(), 1)
        self.assertTrue(sc_set)

    async def test_get_power_empty(self):
        sc_set = await AScOrientedSet.create()
        self.assertEqual(await sc_set.len(), 0)
        self.assertTrue(await sc_set.is_empty())

    async def test_contains(self):
        element_in = await create_node(sc_types.NODE_CONST)
        element_not_in = await create_node(sc_types.NODE_CONST)
        sc_set = await AScOrientedSet.create(element_in)
        self.assertTrue(await sc_set.contains(element_in))
        self.assertFalse(await sc_set.contains(element_not_in))

    async def test_remove(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element_to_remove = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScOrientedSet.create(element1, element_to_remove, element2)
        self.assertEqual(await sc_set.len(), 3)
        await sc_set.remove(element_to_remove)
        self.assertEqual(await sc_set.len(), 2)
        self.assertEqual(await sc_set.elements_list, [element1, element2])
        await sc_set.clear()
        self.assertTrue(await sc_set.is_empty())
        self.assertEqual(await sc_set.elements_list, [])

    async def _assert_two_elements_oriented_set_template(
        self, set_node: ScAddr, start_element: ScAddr, other_element: ScAddr
    ) -> None:
        edge1, edge2 = "edge1", "edge2"
        template = ScTemplate()
        template.triple_with_relation(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM >> edge1,
            start_element,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            await asc_keynodes.rrel_index(1),
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
            await asc_keynodes.get_valid(CommonIdentifiers.NREL_BASIC_SEQUENCE),
        )
        results = await asc_client.template_search(template)
        self.assertEqual(len(results), 1)
