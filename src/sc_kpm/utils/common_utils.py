"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from typing import List, Optional, Union

import sc_client
from sc_client.constants import sc_types
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScConstruction, ScLinkContent, ScLinkContentType, ScTemplate, ScTemplateResult
from sc_client.models.sc_construction import ScLinkContentData
from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_keynodes import Idtf, ScKeynodes


def create_nodes(*node_types: ScType) -> List[ScAddr]:
    construction = ScConstruction()
    for node_type in node_types:
        construction.create_node(node_type)
    return sc_client.create_elements(construction)


def create_node(node_type: ScType) -> ScAddr:
    return create_nodes(node_type)[0]


def create_links(
    *contents: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_types.LINK_CONST,
) -> List[ScAddr]:
    construction = ScConstruction()
    for content in contents:
        link_content = ScLinkContent(content, content_type)
        construction.create_link(link_type, link_content)
    return sc_client.create_elements(construction)


def create_link(
    content: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_types.LINK_CONST,
) -> ScAddr:
    return create_links(content, content_type=content_type, link_type=link_type)[0]


def create_edge(edge_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr:
    return create_edges(edge_type, src, trg)[0]


def create_edges(edge_type: ScType, src: ScAddr, *targets: ScAddr) -> List[ScAddr]:
    construction = ScConstruction()
    for trg in targets:
        construction.create_edge(edge_type, src, trg)
    return sc_client.create_elements(construction)


def create_binary_relation(edge_type: ScType, src: ScAddr, trg: ScAddr, *relations: ScAddr) -> ScAddr:
    construction = ScConstruction()
    construction.create_edge(edge_type, src, trg, ScAlias.RELATION_EDGE)
    for relation in relations:
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, relation, ScAlias.RELATION_EDGE)
    return sc_client.create_elements(construction)[0]


def create_role_relation(src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> ScAddr:
    return create_binary_relation(sc_types.EDGE_ACCESS_CONST_POS_PERM, src, trg, *rrel_nodes)


def create_norole_relation(src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> ScAddr:
    return create_binary_relation(sc_types.EDGE_D_COMMON_CONST, src, trg, *nrel_nodes)


def check_edge(edge_type: ScType, source: ScAddr, target: ScAddr) -> bool:
    return bool(get_edges(source, target, edge_type))


def get_edge(source: ScAddr, target: ScAddr, edge_type: ScType) -> ScAddr:
    edges = get_edges(source, target, edge_type)
    return edges[0] if edges else ScAddr(0)


def get_edges(source: ScAddr, target: ScAddr, *edge_types: ScType) -> List[ScAddr]:
    result_edges = []
    for edge_type in edge_types:
        templ = ScTemplate()
        templ.triple(source, edge_type, target)
        results = sc_client.template_search(templ)
        result_edges.extend(result[1] for result in results)
    return result_edges


def get_system_idtf(addr: ScAddr) -> Idtf:
    nrel_system_idtf = ScKeynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER]

    templ = ScTemplate()
    templ.triple_with_relation(
        addr,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> ScAlias.LINK,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        nrel_system_idtf,
    )
    result = sc_client.template_search(templ)
    if result:
        return get_link_content_data(result[0].get(ScAlias.LINK))
    return ""


def _search_relation_template(src: ScAddr, rel_node: ScAddr, rel_type: ScType) -> Optional[ScTemplateResult]:
    template = ScTemplate()
    template.triple_with_relation(
        src,
        rel_type >> ScAlias.ACCESS_EDGE,
        sc_types.UNKNOWN >> ScAlias.ELEMENT,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        rel_node,
    )
    result = sc_client.template_search(template)
    return result[0] if result else None


def search_role_relation_template(src: ScAddr, rrel_node: ScAddr) -> Optional[ScTemplateResult]:
    return _search_relation_template(src, rrel_node, sc_types.EDGE_ACCESS_VAR_POS_PERM)


def search_norole_relation_template(src: ScAddr, nrel_node: ScAddr) -> Optional[ScTemplateResult]:
    return _search_relation_template(src, nrel_node, sc_types.EDGE_D_COMMON_VAR)


def get_element_by_role_relation(src: ScAddr, rrel_node: ScAddr) -> ScAddr:
    search_result = search_role_relation_template(src, rrel_node)
    return search_result.get(ScAlias.ELEMENT) if search_result else ScAddr(0)


def get_element_by_norole_relation(src: ScAddr, nrel_node: ScAddr) -> ScAddr:
    search_result = search_norole_relation_template(src, nrel_node)
    return search_result.get(ScAlias.ELEMENT) if search_result else ScAddr(0)


def get_link_content_data(link: ScAddr) -> ScLinkContentData:
    content_part = sc_client.get_link_content(link)
    return content_part[0].data


def delete_edges(source: ScAddr, target: ScAddr, *edge_types: ScType) -> bool:
    return sc_client.delete_elements(*get_edges(source, target, *edge_types))
