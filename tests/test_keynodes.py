from common_tests import BaseTestCase

from sc_client import client
from sc_client.client import check_elements, delete_elements
from sc_client.constants import sc_types
from sc_client.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScIdtfResolveParams
from sc_kpm import ScKeynodes


class KeynodesTests(BaseTestCase):
    def test_get_existed_keynode(self):
        idtf = "idtf_existed_keynode"
        params = ScIdtfResolveParams(idtf, sc_types.NODE_CONST)
        addr = client.resolve_keynodes(params)[0]
        result = ScKeynodes[idtf]
        self.assertEqual(result, addr)

    def test_get_unknown_idtf(self):
        idtf = "idtf_unknown_idtf"
        self.assertRaises(InvalidValueError, ScKeynodes.__getitem__, idtf)
        self.assertEqual(ScKeynodes.get(idtf), ScAddr(0))

    def test_resolve_keynode(self):
        idtf = "idtf_new_keynode"
        addr = ScKeynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(delete_elements(addr))
        self.assertTrue(addr.is_valid())

    def test_delete_keynode(self):
        idtf = "idtf_to_delete_keynode"
        ScKeynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(ScKeynodes.delete(idtf))
        self.assertFalse(ScKeynodes.get(idtf).is_valid())
        self.assertRaises(InvalidValueError, ScKeynodes.delete, idtf)

    def test_keynodes_initialization(self):
        self.assertRaises(TypeError, ScKeynodes)

    def test_rrel(self):
        rrel_1 = ScKeynodes.rrel_index(1)
        self.assertTrue(rrel_1.is_valid())
        self.assertTrue(check_elements(rrel_1)[0].is_role())

    def test_large_rrel(self):
        self.assertRaises(KeyError, ScKeynodes.rrel_index, ScKeynodes._max_rrel_index + 1)

    def test_wrong_rrel(self):
        self.assertRaises(TypeError, ScKeynodes.rrel_index, "str")
