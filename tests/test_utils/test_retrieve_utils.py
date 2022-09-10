"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants import sc_types

from sc_kpm.utils.common_utils import create_link, create_node
from sc_kpm.utils.creation_utils import wrap_in_oriented_set, wrap_in_set
from sc_kpm.utils.retrieve_utils import get_oriented_set_elements, get_set_elements, get_set_power
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
        assert search_results == elements

    def test_get_set_elements_empty(self):
        set_node = create_node(sc_types.NODE_CONST)
        search_results = get_set_elements(set_node)
        assert search_results == []

    def test_get_oriented_set_elements(self):
        set_node = create_node(sc_types.NODE_CONST)
        elements = [
            create_node(sc_types.NODE_CONST),
            create_link("abc"),
            create_node(sc_types.NODE_CONST),
        ]
        wrap_in_oriented_set(set_node, *elements)
        search_results = get_oriented_set_elements(set_node)
        assert search_results == elements

    def test_get_oriented_set_elements_empty(self):
        set_node = create_node(sc_types.NODE_CONST)
        search_results = get_oriented_set_elements(set_node)
        assert search_results == []

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

    def test_get_set_power_empty(self):
        set_node = create_node(sc_types.NODE_CONST)
        search_results = get_set_power(set_node)
        assert search_results == 0
