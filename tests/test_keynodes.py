from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.exceptions import InvalidValueError
from sc_client.models import ScIdtfResolveParams, ScAddr

from common_tests import BaseTestCase
from sc_kpm import ScKeynodes


class KeynodesTests(BaseTestCase):
    keynodes = ScKeynodes()

    def test_get_existed_keynode(self):
        idtf = "idtf_existed_keynode"
        params = ScIdtfResolveParams(idtf=idtf, type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes(params)[0]
        result = self.keynodes[idtf]
        self.assertEqual(result, addr)

    def test_get_unknown_idtf(self):
        idtf = "idtf_unknown_idtf"
        self.assertRaises(InvalidValueError, self.keynodes.__getitem__, idtf)
        self.assertEqual(self.keynodes.get(idtf), ScAddr(0))

    def test_resolve_keynode(self):
        idtf_format = "idtf_resolve_{}"
        i: int = 1
        while self.keynodes.get(idtf := idtf_format.format(i)).is_valid():
            i += 1
        addr = self.keynodes.resolve(idtf, sc_types.NODE_CONST)
        self.assertTrue(addr.is_valid())
        del self.keynodes._dict[idtf]
        self.assertEqual(self.keynodes.get(idtf), addr)
