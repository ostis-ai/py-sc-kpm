"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""
import logging
from typing import List, Optional

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScConstruction, ScIdtfResolveParams, ScLinkContent, ScLinkContentType, ScTemplate, \
    ScTemplateResult

from sc_common.identifiers import ScAlias, CommonIdentifiers
from sc_common.sc_keynodes import ScKeynodes


def generate_nodes(*node_types: ScType) -> List[ScAddr]:
    construction = ScConstruction()
    for node_type in node_types:
        construction.create_node(node_type)
    return client.create_elements(construction)


def generate_node(node_type: ScType, sys_idtf: str = None) -> ScAddr:
    if sys_idtf:
        params = ScIdtfResolveParams(idtf=sys_idtf, type=node_type)
        return client.resolve_keynodes(params)[0]
    return generate_nodes(node_type)[0]


def generate_links(*contents: str) -> List[ScAddr]:
    construction = ScConstruction()
    for content in contents:
        link_content = ScLinkContent(content, ScLinkContentType.STRING.value)
        construction.create_link(sc_types.LINK, link_content)
    return client.create_elements(construction)


def generate_link(content: str) -> ScAddr:
    return generate_links(content)[0]


def generate_edge(src: ScAddr, edge_type: ScType, trg: ScAddr) -> ScAddr:
    construction = ScConstruction()
    construction.create_edge(edge_type, src, trg)
    return client.create_elements(construction)[0]


def generate_binary_relation(src: ScAddr, edge_type: ScType, trg: ScAddr, *relations: ScAddr) -> ScAddr:
    construction = ScConstruction()
    construction.create_edge(edge_type, src, trg, ScAlias.RELATION_EDGE.value)
    for relation in relations:
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, relation, ScAlias.RELATION_EDGE.value)
    return client.create_elements(construction)[0]


def generate_role_relation(src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> ScAddr:
    return generate_binary_relation(src, sc_types.EDGE_ACCESS_CONST_POS_PERM, trg, *rrel_nodes)


def generate_norole_relation(src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> ScAddr:
    return generate_binary_relation(src, sc_types.EDGE_D_COMMON_CONST, trg, *nrel_nodes)


def check_edge(source: ScAddr, edge_type: ScType, target: ScAddr) -> bool:
    return get_edge(source, edge_type, target).is_valid()


def get_edges(source: ScAddr, edge_type: ScType, target: ScAddr) -> List[ScAddr]:
    templ = ScTemplate()
    templ.triple(source, edge_type, target)
    results = client.template_search(templ)
    logging.debug(results)
    return [result.get(1) for result in results]


def get_edge(source: ScAddr, edge_type: ScType, target: ScAddr) -> ScAddr:
    edges = get_edges(source, edge_type, target)
    return edges[0] if len(edges) > 0 else ScAddr(0)


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
    result = client.template_search(templ)
    if len(result) > 0:
        return get_link_content(result[0].get(ScAlias.LINK.value))
    return ""


def search_role_relation_template(src: ScAddr, rrel_node: ScAddr) -> Optional[ScTemplateResult]:
    templ = ScTemplate()
    templ.triple_with_relation(
        src,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAlias.ACCESS_EDGE.value],
        [sc_types.UNKNOWN, ScAlias.ELEMENT.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        rrel_node,
    )
    result = client.template_search(templ)
    return result[0] if len(result) > 0 else None


def get_element_by_role_relation(src: ScAddr, rrel_node: ScAddr) -> ScAddr:
    search_result = search_role_relation_template(src, rrel_node)
    return search_result.get(ScAlias.ELEMENT.value) if search_result else ScAddr(0)


def get_link_content(link: ScAddr) -> str:
    content_part = client.get_link_content(link)
    return content_part[0].data


def delete_elements(*addrs: ScAddr) -> bool:
    return client.delete_elements(*addrs)


def delete_edge(source: ScAddr, edge_type: ScType, target: ScAddr) -> bool:
    return delete_elements(*get_edges(source, edge_type, target))

