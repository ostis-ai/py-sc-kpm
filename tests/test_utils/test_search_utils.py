"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from typing import List

from sc_client.constants import sc_types
from sc_client.models import ScAddr

from sc_kpm.utils.common_utils import create_link, create_node
from sc_kpm.utils.generation_utils import wrap_in_oriented_set, wrap_in_set
from sc_kpm.utils.search_utils import get_oriented_set_elements, get_set_elements, get_set_power
from tests.common_tests import BaseTestCase


class TestSearchUtils(BaseTestCase):
    def test_get_set_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        wrap_in_set(set_node, *elements)
        search_results = get_set_elements(set_node)
        assert are_elements_equal(search_results, elements)

    def test_get_oriented_set_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        wrap_in_oriented_set(set_node, *elements)
        search_results = get_oriented_set_elements(set_node)
        assert are_elements_equal(search_results, elements)

    def test_get_set_power(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        wrap_in_set(set_node, *elements)
        search_results = get_set_power(set_node)
        assert search_results == len(elements)


def are_elements_equal(elements1: List[ScAddr], elements2: List[ScAddr]):
    """Temporary while ScAddr don't have __eq__ method"""
    if len(elements1) != len(elements2):
        return False
    for addr1, addr2 in zip(elements1, elements2):
        if addr1.value != addr2.value:
            return False
    return True
