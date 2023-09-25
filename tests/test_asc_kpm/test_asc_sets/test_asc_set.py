"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScTemplate
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.asc_sets import AScSet
from asc_kpm.utils import create_node


class AScSetTestCase(AsyncioScKpmTestCase):
    async def test_create_with_set_node(self):
        set_node = await create_node(sc_types.NODE_CONST)
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        await AScSet.create(element1, element2, set_node=set_node)
        await self._assert_two_elements_set_template(set_node, element1, element2)

    async def test_create_without_set_node(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create(element1, element2)
        self.assertEqual((await asc_client.check_elements(sc_set.set_node))[0], sc_types.NODE_CONST)
        await self._assert_two_elements_set_template(sc_set.set_node, element1, element2)

    async def test_create_with_set_type(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create(element1, element2, set_node_type=sc_types.NODE_CONST_STRUCT)
        self.assertEqual((await asc_client.check_elements(sc_set.set_node))[0], sc_types.NODE_CONST_STRUCT)
        await self._assert_two_elements_set_template(sc_set.set_node, element1, element2)

    async def test_create_copy_set_node(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create(element1, element2)
        sc_set_copy = await AScSet.create(set_node=sc_set.set_node)
        self.assertEqual(sc_set, sc_set_copy)
        await self._assert_two_elements_set_template(sc_set_copy.set_node, element1, element2)

    async def test_get_elements_set(self):
        elements = {await create_node(sc_types.NODE_CONST), await create_node(sc_types.NODE_CONST)}
        sc_set = await AScSet.create(*elements)
        self.assertEqual(await sc_set.elements_set, elements)

    async def test_get_elements_set_empty(self):
        sc_set = await AScSet.create()
        self.assertEqual(await sc_set.elements_set, set())

    async def test_iterate(self):
        elements = {await create_node(sc_types.NODE_CONST), await create_node(sc_types.NODE_CONST)}
        sc_set = await AScSet.create(*elements)
        async for set_element in sc_set:
            self.assertIn(set_element, elements)

    async def test_add(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create(element1)
        await sc_set.add(element2)
        self.assertEqual((await asc_client.check_elements(sc_set.set_node))[0], sc_types.NODE_CONST)
        await self._assert_two_elements_set_template(sc_set.set_node, element1, element2)

    async def test_add_element_twice(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        elements = {element1, element2}
        sc_set = await AScSet.create(*elements)
        await sc_set.add(element2)  # element is added second time
        self.assertEqual(await sc_set.elements_set, elements)  # element1 will not duplicate

    async def test_get_power(self):
        element = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create()
        self.assertEqual(await sc_set.len(), 0)
        await sc_set.add(element)
        self.assertEqual(await sc_set.len(), 1)

    async def test_booleans(self):
        """Test __bool__(), is_empty() and __contains__"""
        sc_set = await AScSet.create()
        self.assertTrue(await sc_set.is_empty())

        element = await create_node(sc_types.NODE_CONST)
        await sc_set.add(element)
        self.assertFalse(await sc_set.is_empty())

        self.assertTrue(await sc_set.contains(element))
        self.assertFalse(await sc_set.contains(ScAddr(0)))

    async def test_remove(self):
        element = await create_node(sc_types.NODE_CONST)
        element_to_remove = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create(element, element_to_remove)
        self.assertEqual(await sc_set.len(), 2)
        await sc_set.remove(element_to_remove)
        self.assertEqual(await sc_set.len(), 1)
        self.assertEqual(await sc_set.elements_set, {element})

    async def test_clear(self):
        element1 = await create_node(sc_types.NODE_CONST)
        element2 = await create_node(sc_types.NODE_CONST)
        sc_set = await AScSet.create(element1, element2)
        self.assertFalse(await sc_set.is_empty())
        await sc_set.clear()
        self.assertTrue(await sc_set.is_empty())

    async def _assert_two_elements_set_template(self, set_node: ScAddr, element1: ScAddr, element2: ScAddr) -> None:
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
        results = await asc_client.template_search(template)
        self.assertEqual(len(results), 1)
