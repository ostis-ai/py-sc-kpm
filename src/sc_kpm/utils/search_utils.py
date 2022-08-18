"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from typing import List, Optional

from sc_client import client
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate, ScTemplateResult

from sc_kpm import ScKeynodes
from sc_kpm.common import CommonIdentifiers, ScAlias
from sc_kpm.utils.common_utils import get_link_content, search_role_relation_template


def get_set_elements(set_node: ScAddr) -> List[ScAddr]:
    elements = []
    for target in (sc_types.LINK_VAR, sc_types.NODE_VAR):
        templ = ScTemplate()
        templ.triple(set_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, target)
        search_results = client.template_search(templ)
        for result in search_results:
            elements.append(result.get(2))
    return elements


def get_oriented_set_elements(set_node: ScAddr) -> List[ScAddr]:
    def get_next_element(access_edge: ScAddr = None):
        if access_edge:
            elem_search_result = _search_next_element_template(set_node, access_edge)
        else:
            keynodes = ScKeynodes()
            elem_search_result = search_role_relation_template(set_node, keynodes[CommonIdentifiers.RREL_ONE.value])
        if elem_search_result is None:
            return None
        elements.append(elem_search_result.get(ScAlias.ELEMENT.value))
        return elem_search_result.get(ScAlias.ACCESS_EDGE.value)

    elements = []
    elements_count = get_set_power(set_node)
    if elements_count:
        edge = get_next_element()
        while edge:
            edge = get_next_element(edge)
    return elements


def _search_next_element_template(set_node: ScAddr, cur_element_edge: ScAddr) -> Optional[ScTemplateResult]:
    keynodes = ScKeynodes()
    templ = ScTemplate()
    templ.triple_with_relation(
        cur_element_edge,
        sc_types.EDGE_D_COMMON_VAR,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAlias.ACCESS_EDGE.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE.value],
    )
    templ.triple(set_node, ScAlias.ACCESS_EDGE.value, [sc_types.UNKNOWN, ScAlias.ELEMENT.value])
    return _get_first_search_template_result(templ)


def _get_first_search_template_result(template: ScTemplate) -> Optional[ScTemplateResult]:
    search_results = client.template_search(template)
    if search_results:
        return search_results[0]
    return None


def get_set_power(source: ScAddr) -> int:
    templ = ScTemplate()
    templ.triple(source, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.UNKNOWN)
    search_results = client.template_search(templ)
    return len(search_results)
