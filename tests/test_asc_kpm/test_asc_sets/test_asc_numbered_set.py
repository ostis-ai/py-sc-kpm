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
from asc_kpm.asc_sets import AScNumberedSet
from asc_kpm.utils import create_link, create_node, create_nodes


class ScNumberedSetTestCase(AsyncioScKpmTestCase):
    async def test_create_with_set_node(self):
        set_node = await create_node(sc_types.NODE_CONST)
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        await AScNumberedSet.create(element1, element2, set_node=set_node)
        await self._assert_two_elements_num_set_template(set_node, element1, element2)

    async def test_create_without_set_node(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element1, element2)
        await self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    async def test_create_with_set_type(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element1, element2, set_node_type=sc_types.NODE_CONST_STRUCT)
        self.assertEqual((await asc_client.check_elements(sc_set.set_node))[0], sc_types.NODE_CONST_STRUCT)
        await self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    async def test_create_large(self):
        elements = await create_nodes(*[sc_types.NODE_CONST] * 3)
        sc_set = await AScNumberedSet.create(*elements)
        self.assertEqual(await sc_set.elements_list, elements)

    async def test_create_copy_num_set_node(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element1, element2)
        sc_set_copy = await AScNumberedSet.create(set_node=sc_set.set_node)
        await self._assert_two_elements_num_set_template(sc_set_copy.set_node, element1, element2)

    async def test_add(self):
        element1 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element1)
        element2 = await create_node(sc_types.NODE_CONST)
        await sc_set.add(element2)
        await self._assert_two_elements_num_set_template(sc_set.set_node, element1, element2)

    async def test_iterate(self):
        set_node = await create_node(sc_types.NODE_CONST)
        elements = [
            await create_node(sc_types.NODE_CONST),
            await create_link("abc"),
            await create_node(sc_types.NODE_CONST),
        ]
        sc_set = await AScNumberedSet.create(*elements, set_node=set_node)
        self.assertEqual([element async for element in sc_set], elements)

    async def test_get_elements(self):
        set_node = await create_node(sc_types.NODE_CONST)
        elements = [
            await create_node(sc_types.NODE_CONST),
            await create_link("abc"),
            await create_node(sc_types.NODE_CONST),
        ]
        sc_set = await AScNumberedSet.create(*elements, set_node=set_node)
        self.assertEqual(await sc_set.elements_list, elements)

    async def test_get_elements_empty(self):
        sc_set = await AScNumberedSet.create()
        self.assertEqual(await sc_set.elements_list, [])

    async def test_get_power(self):
        set_node = await create_node(sc_types.NODE_CONST)
        elements = [
            await create_node(sc_types.NODE_CONST),
            await create_link("abc"),
            await create_node(sc_types.NODE_CONST),
        ]
        sc_set = await AScNumberedSet.create(*elements, set_node=set_node)
        self.assertEqual(await sc_set.len(), len(elements))
        self.assertTrue(sc_set)

    async def test_get_power_empty(self):
        sc_set = await AScNumberedSet.create()
        self.assertEqual(await sc_set.len(), 0)
        self.assertTrue(await sc_set.is_empty())

    async def test_get_by_index(self):
        element0 = await create_node(sc_types.NODE_CONST)
        element1 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element0, element1)
        self.assertEqual(await sc_set.at(0), element0)
        self.assertEqual(await sc_set.at(1), element1)
        with self.assertRaises(KeyError):
            await sc_set.at(2)

    async def test_contain(self):
        element_in = await create_node(sc_types.NODE_CONST)
        element_not_in = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element_in)
        self.assertTrue(await sc_set.contains(element_in))
        self.assertFalse(await sc_set.contains(element_not_in))

    async def test_remove(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element_to_remove = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScNumberedSet.create(element1, element_to_remove, element2)
        self.assertEqual(await sc_set.len(), 3)
        await sc_set.remove(element_to_remove)
        self.assertEqual(await sc_set.len(), 2)
        self.assertEqual(await sc_set.elements_list, [element1, element2])
        await sc_set.clear()
        self.assertTrue(await sc_set.is_empty())
        self.assertEqual(await sc_set.elements_list, [])

    async def _assert_two_elements_num_set_template(self, set_node: ScAddr, element1: ScAddr, element2: ScAddr) -> None:
        template = ScTemplate()
        template.triple_with_relation(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            element1,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            await asc_keynodes.rrel_index(1),
        )
        template.triple_with_relation(
            set_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            element2,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            await asc_keynodes.rrel_index(2),
        )
        results = await asc_client.template_search(template)
        self.assertEqual(len(results), 1)
