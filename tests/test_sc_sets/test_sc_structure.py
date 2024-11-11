"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.client import check_elements
from sc_client.constants import sc_type
from sc_client.constants.exceptions import InvalidTypeError

from sc_kpm.sc_sets import ScSet, ScStructure
from sc_kpm.utils.common_utils import generate_node
from tests.common_tests import BaseTestCase


class ScStructureTestCase(BaseTestCase):
    def test_is_sc_set_child(self):
        """Save sc-set methods"""
        self.assertIsInstance(ScStructure(), ScSet)

    def test_create(self):
        struct = ScStructure()
        self.assertTrue(check_elements(struct.set_node)[0] == sc_type.CONST_NODE_STRUCTURE)

    def test_create_valid_type(self):
        node_var_struct = generate_node(sc_type.NODE_VAR_STRUCT)
        self.assertIsNotNone(ScStructure(set_node_type=sc_type.NODE_VAR_STRUCT))
        self.assertIsNotNone(ScStructure(set_node=node_var_struct))

    def test_create_wrong_type(self):
        self.assertRaises(InvalidTypeError, ScStructure, set_node_type=sc_type.CONST_NODE)

    def test_create_wrong_struct_node(self):
        node_const = generate_node(sc_type.CONST_NODE)
        self.assertRaises(InvalidTypeError, ScStructure, set_node=node_const)
