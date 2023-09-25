"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.sc_exceptions import InvalidTypeError
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.asc_sets import AScSet, AScStructure
from asc_kpm.utils import create_node


class AScStructureTestCase(AsyncioScKpmTestCase):
    async def test_is_sc_set_child(self):
        """Save sc-set methods"""
        self.assertIsInstance(await AScStructure.create(), AScSet)

    async def test_create(self):
        struct = await AScStructure.create()
        self.assertTrue((await asc_client.check_elements(struct.set_node))[0] == sc_types.NODE_CONST_STRUCT)

    async def test_create_valid_type(self):
        node_var_struct = await create_node(sc_types.NODE_VAR_STRUCT)
        self.assertIsNotNone(await AScStructure.create(set_node_type=sc_types.NODE_VAR_STRUCT))
        self.assertIsNotNone(await AScStructure.create(set_node=node_var_struct))

    async def test_create_wrong_type(self):
        with self.assertRaises(InvalidTypeError):
            await AScStructure.create(set_node_type=sc_types.NODE_CONST)

    async def test_create_wrong_struct_node(self):
        node_const = await create_node(sc_types.NODE_CONST)
        with self.assertRaises(InvalidTypeError):
            await AScStructure.create(set_node=node_const)
