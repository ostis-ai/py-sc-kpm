"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from typing import List, Optional

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScTemplate, ScTemplateResult

from sc_common.identifiers import CommonIdentifiers
from sc_common.sc_keynodes import ScKeynodes
from sc_utils.constants import ScAlias
from sc_utils.templates import template_next_element_of_oriented_set


def check_edge(source: ScAddr, target: ScAddr, edge_type: ScType) -> bool:
    templ = ScTemplate()
    templ.triple(source, edge_type, target)
    search_results = client.template_search(templ)
    return len(search_results) > 0


def get_system_idtf(addr: ScAddr) -> str:
    keynodes = ScKeynodes()
    nrel_system_idtf = keynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER.value]

    templ = ScTemplate()
    templ.triple_with_relation(
        addr,
        sc_types.EDGE_D_COMMON_VAR,
        [sc_types.LINK_VAR, ScAlias.LINK.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        nrel_system_idtf,
    )
    result = get_first_search_template_result(templ)
    if result:
        return get_link_content(result.get(ScAlias.LINK.value))
    return ""


def get_power_of_set(source: ScAddr) -> int:
    edge_type = sc_types.EDGE_ACCESS_VAR_POS_PERM
    target = sc_types.UNKNOWN
    templ = ScTemplate()
    templ.triple(source, edge_type, target)
    search_results = client.template_search(templ)
    return len(search_results)


def get_element_by_role_relation(src: ScAddr, role: ScAddr) -> Optional[ScAddr]:
    search_result = search_role_relation_template(src, role)
    return search_result.get(ScAlias.ELEMENT.value) if search_result else None


def search_role_relation_template(src: ScAddr, role: ScAddr) -> Optional[ScTemplateResult]:
    templ = ScTemplate()
    templ.triple_with_relation(
        src,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAlias.ACCESS_EDGE.value],
        [sc_types.UNKNOWN, ScAlias.ELEMENT.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        role,
    )
    return get_first_search_template_result(templ)


def get_structure_elements(structure: ScAddr) -> List[ScAddr]:
    structure_elements = []
    for target in (sc_types.LINK_VAR, sc_types.NODE_VAR):
        templ = ScTemplate()
        templ.triple(structure, sc_types.EDGE_ACCESS_VAR_POS_PERM, target)
        search_results = client.template_search(templ)
        for result in search_results:
            structure_elements.append(result.get(2))
    return structure_elements


def get_elements_from_oriented_set(set_node: ScAddr) -> List[ScAddr]:
    def get_next_element(access_edge: ScAddr = None):
        if access_edge:
            elem_search_result = search_next_element_template(set_node, access_edge)
        else:
            keynodes = ScKeynodes()
            elem_search_result = search_role_relation_template(set_node, keynodes[CommonIdentifiers.RREL_ONE.value])
        if elem_search_result is None:
            return None
        elements.append(elem_search_result.get(ScAlias.ELEMENT.value))
        return elem_search_result.get(ScAlias.ACCESS_EDGE.value)

    elements = []
    elements_count = get_power_of_set(set_node)
    if elements_count:
        edge = get_next_element()
        while edge:
            edge = get_next_element(edge)
    return elements


def search_next_element_template(set_node: ScAddr, prev_element_edge: ScAddr) -> Optional[ScTemplateResult]:
    templ = template_next_element_of_oriented_set(set_node, prev_element_edge)
    return get_first_search_template_result(templ)


def get_first_search_template_result(template: ScTemplate) -> Optional[ScTemplateResult]:
    search_results = client.template_search(template)
    if len(search_results) > 0:
        return search_results[0]
    return None


def get_content_from_links_set(links_set_node: ScAddr) -> str:
    links = get_elements_from_oriented_set(links_set_node)
    parts = []
    for link in links:
        parts.append(get_link_content(link))
    return "".join(parts)


def get_link_content(link: ScAddr) -> str:
    content_part = client.get_link_content(link)
    return content_part.data


def get_action_answer(action: ScAddr) -> ScAddr:
    templ = ScTemplate()
    keynodes = ScKeynodes()
    templ.triple_with_relation(
        action,
        [sc_types.EDGE_D_COMMON_VAR, ScAlias.RELATION_EDGE.value],
        [sc_types.NODE_VAR_STRUCT, ScAlias.ELEMENT.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes[CommonIdentifiers.NREL_ANSWER.value],
    )
    result = get_first_search_template_result(templ)
    return result.get(ScAlias.ELEMENT.value) if result else ScAddr(0)
