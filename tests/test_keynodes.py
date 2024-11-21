from common_tests import BaseTestCase
from sc_client import client
from sc_client.client import erase_elements, get_elements_types
from sc_client.constants import sc_type
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScIdtfResolveParams

from sc_kpm import ScKeynodes


class KeynodesTests(BaseTestCase):
    def test_get_existed_keynode(self):
        idtf = "idtf_existed_keynode"
        params = ScIdtfResolveParams(idtf=idtf, type=sc_type.CONST_NODE)
        addr = client.resolve_keynodes(params)[0]
        result = ScKeynodes[idtf]
        self.assertEqual(result, addr)

    def test_get_unknown_idtf(self):
        idtf = "idtf_unknown_idtf"
        self.assertRaises(InvalidValueError, ScKeynodes.__getitem__, idtf)
        self.assertEqual(ScKeynodes.get(idtf), ScAddr(0))

    def test_resolve_keynode(self):
        idtf = "idtf_new_keynode"
        addr = ScKeynodes.resolve(idtf, sc_type.CONST_NODE)
        self.assertTrue(erase_elements(addr))
        self.assertTrue(addr.is_valid())

    def test_erase_keynode(self):
        idtf = "idtf_to_erase_keynode"
        ScKeynodes.resolve(idtf, sc_type.CONST_NODE)
        self.assertTrue(ScKeynodes.erase(idtf))
        self.assertFalse(ScKeynodes.get(idtf).is_valid())
        self.assertRaises(InvalidValueError, ScKeynodes.erase, idtf)

    def test_keynodes_initialization(self):
        self.assertRaises(TypeError, ScKeynodes)

    def test_rrel(self):
        rrel_1 = ScKeynodes.rrel_index(1)
        self.assertTrue(rrel_1.is_valid())
        self.assertTrue(get_elements_types(rrel_1)[0].is_role())

    def test_max_rrel(self):
        self.assertRaises(KeyError, ScKeynodes.rrel_index, ScKeynodes._max_rrel_index + 1)

    def test_min_rrel(self):
        self.assertRaises(KeyError, ScKeynodes.rrel_index, ScKeynodes._min_rrel_index - 1)

    def test_wrong_rrel(self):
        self.assertRaises(TypeError, ScKeynodes.rrel_index, "str")
