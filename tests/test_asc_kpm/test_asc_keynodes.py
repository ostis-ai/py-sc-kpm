from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScIdtfResolveParams
from sc_client.sc_exceptions import InvalidValueError
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.asc_keynodes_ import asc_keynodes


class KeynodesTests(AsyncioScKpmTestCase):
    async def test_get_existed_keynode(self):
        idtf = "idtf_existed_keynode"
        params = ScIdtfResolveParams(idtf=idtf, type=sc_types.NODE_CONST)
        addr = (await asc_client.resolve_keynodes(params))[0]
        result = await asc_keynodes.get_valid(idtf)
        self.assertEqual(result, addr)

    async def test_get_unknown_idtf(self):
        idtf = "idtf_unknown_idtf"
        with self.assertRaises(InvalidValueError):
            await asc_keynodes.get_valid(idtf)
        self.assertEqual(await asc_keynodes.get(idtf), ScAddr(0))

    async def test_resolve_keynode(self):
        idtf = "idtf_new_keynode"
        addr = await asc_keynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(await asc_client.delete_elements(addr))
        self.assertTrue(addr.is_valid())

    async def test_delete_keynode(self):
        idtf = "idtf_to_delete_keynode"
        await asc_keynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(await asc_keynodes.delete(idtf))
        self.assertFalse((await asc_keynodes.get(idtf)).is_valid())
        with self.assertRaises(InvalidValueError):
            await asc_keynodes.delete(idtf)

    async def test_rrel(self):
        rrel_1 = await asc_keynodes.rrel_index(1)
        self.assertTrue(rrel_1.is_valid())
        self.assertTrue((await asc_client.check_elements(rrel_1))[0].is_role())

    async def test_large_rrel(self):
        with self.assertRaises(KeyError):
            await asc_keynodes.rrel_index(asc_keynodes._max_rrel_index + 1)

    async def test_wrong_rrel(self):
        with self.assertRaises(TypeError):
            await asc_keynodes.rrel_index("str")
