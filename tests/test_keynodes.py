from common_tests import BaseTestCase

from sc_client import ScAddr, sc_types
from sc_client.init import sc_client, sc_keynodes
from sc_client.models import ScIdtfResolveParams
from sc_client.sc_exceptions import InvalidValueError


class KeynodesTests(BaseTestCase):
    def test_get_existed_keynode(self):
        idtf = "idtf_existed_keynode"
        params = ScIdtfResolveParams(idtf, sc_types.NODE_CONST)
        addr = sc_client.resolve_keynodes(params)[0]
        result = sc_keynodes[idtf]
        self.assertEqual(result, addr)

    def test_resolve_no_keynode(self):
        addrs = sc_client.resolve_keynodes()
        self.assertEqual([], addrs)

    def test_get_unknown_idtf(self):
        idtf = "idtf_unknown_idtf"
        self.assertRaises(InvalidValueError, sc_keynodes.__getitem__, idtf)
        self.assertEqual(sc_keynodes.get(idtf), ScAddr(0))

    def test_resolve_keynode(self):
        idtf = "idtf_new_keynode"
        addr = sc_keynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(sc_client.delete_elements(addr))
        self.assertTrue(addr.is_valid())

    def test_delete_keynode(self):
        idtf = "idtf_to_delete_keynode"
        sc_keynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(sc_keynodes.delete(idtf))
        self.assertFalse(sc_keynodes.get(idtf).is_valid())
        self.assertRaises(InvalidValueError, sc_keynodes.delete, idtf)

    def test_keynodes_initialization(self):
        self.assertRaises(TypeError, sc_keynodes)

    def test_rrel(self):
        rrel_1 = sc_keynodes.rrel_index(1)
        self.assertTrue(rrel_1.is_valid())
        self.assertTrue(sc_client.check_elements(rrel_1)[0].is_role())

    def test_large_rrel(self):
        self.assertRaises(KeyError, sc_keynodes.rrel_index, sc_keynodes._max_rrel_index + 1)

    def test_wrong_rrel(self):
        self.assertRaises(TypeError, sc_keynodes.rrel_index, "str")
