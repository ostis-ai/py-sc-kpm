from common_tests import BaseTestCase
from sc_client import client
from sc_client.client import delete_elements
from sc_client.constants import sc_types
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScAddr, ScIdtfResolveParams

from sc_kpm import ScKeynodes


class KeynodesTests(BaseTestCase):
    def test_get_existed_keynode(self):
        idtf = "idtf_existed_keynode"
        params = ScIdtfResolveParams(idtf=idtf, type=sc_types.NODE_CONST)
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

    def test_keynodes_initialization(self):
        self.assertRaises(TypeError, ScKeynodes)