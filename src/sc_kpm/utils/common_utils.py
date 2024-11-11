"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from typing import List, Optional, Union

from sc_client import client
from sc_client.constants import sc_type
from sc_client.constants.sc_type import ScType
from sc_client.models import ScAddr, ScConstruction, ScLinkContent, ScLinkContentType, ScTemplate, ScTemplateResult
from sc_client.models.sc_construction import ScLinkContentData

from sc_kpm.identifiers import CommonIdentifiers, ScAlias
from sc_kpm.sc_keynodes import Idtf, ScKeynodes


def generate_nodes(*node_types: ScType) -> List[ScAddr]:
    construction = ScConstruction()
    for node_type in node_types:
        construction.generate_node(node_type)
    return client.generate_elements(construction)


def generate_node(node_type: ScType) -> ScAddr:
    return generate_nodes(node_type)[0]


def generate_links(
    *contents: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_type.CONST_NODE_LINK,
) -> List[ScAddr]:
    construction = ScConstruction()
    for content in contents:
        link_content = ScLinkContent(content, content_type)
        construction.generate_link(link_type, link_content)
    return client.generate_elements(construction)


def generate_link(
    content: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_type.CONST_NODE_LINK,
) -> ScAddr:
    return generate_links(content, content_type=content_type, link_type=link_type)[0]


def generate_connector(connector_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr:
    return generate_connectors(connector_type, src, trg)[0]


def generate_connectors(connector_type: ScType, src: ScAddr, *targets: ScAddr) -> List[ScAddr]:
    construction = ScConstruction()
    for trg in targets:
        construction.generate_connector(connector_type, src, trg)
    return client.generate_elements(construction)


def generate_binary_relation(connector_type: ScType, src: ScAddr, trg: ScAddr, *relations: ScAddr) -> ScAddr:
    construction = ScConstruction()
    construction.generate_connector(connector_type, src, trg, ScAlias.RELATION_ARC)
    for relation in relations:
        construction.generate_connector(sc_type.CONST_PERM_POS_ARC, relation, ScAlias.RELATION_ARC)
    return client.generate_elements(construction)[0]


def generate_role_relation(src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> ScAddr:
    return generate_binary_relation(sc_type.CONST_PERM_POS_ARC, src, trg, *rrel_nodes)


def generate_non_role_relation(src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> ScAddr:
    return generate_binary_relation(sc_type.CONST_COMMON_ARC, src, trg, *nrel_nodes)


def check_connector(connector_type: ScType, source: ScAddr, target: ScAddr) -> bool:
    return bool(get_connectors(source, target, connector_type))


def get_connector(source: ScAddr, target: ScAddr, connector_type: ScType) -> ScAddr:
    connectors = get_connectors(source, target, connector_type)
    return connectors[0] if connectors else ScAddr(0)


def get_connectors(source: ScAddr, target: ScAddr, *connector_types: ScType) -> List[ScAddr]:
    result_connectors = []
    for connector_type in connector_types:
        templ = ScTemplate()
        templ.triple(source, connector_type, target)
        results = client.search_by_template(templ)
        result_connectors.extend(result[1] for result in results)
    return result_connectors


def get_element_system_identifier(addr: ScAddr) -> Idtf:
    nrel_system_idtf = ScKeynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER]

    templ = ScTemplate()
    templ.quintuple(
        addr,
        sc_type.VAR_COMMON_ARC,
        sc_type.LINK_VAR >> ScAlias.LINK,
        sc_type.VAR_PERM_POS_ARC,
        nrel_system_idtf,
    )
    result = client.search_by_template(templ)
    if result:
        return get_link_content_data(result[0].get(ScAlias.LINK))
    return ""


def _search_relation_template(src: ScAddr, rel_node: ScAddr, rel_type: ScType) -> Optional[ScTemplateResult]:
    template = ScTemplate()
    template.quintuple(
        src,
        rel_type >> ScAlias.MEMBERSHIP_ARC,
        sc_type.UNKNOWN >> ScAlias.ELEMENT,
        sc_type.VAR_PERM_POS_ARC,
        rel_node,
    )
    result = client.search_by_template(template)
    return result[0] if result else None


def search_role_relation_template(src: ScAddr, rrel_node: ScAddr) -> Optional[ScTemplateResult]:
    return _search_relation_template(src, rrel_node, sc_type.VAR_PERM_POS_ARC)


def search_non_role_relation_template(src: ScAddr, nrel_node: ScAddr) -> Optional[ScTemplateResult]:
    return _search_relation_template(src, nrel_node, sc_type.VAR_COMMON_ARC)


def get_element_by_role_relation(src: ScAddr, rrel_node: ScAddr) -> ScAddr:
    search_result = search_role_relation_template(src, rrel_node)
    return search_result.get(ScAlias.ELEMENT) if search_result else ScAddr(0)


def get_element_by_non_role_relation(src: ScAddr, nrel_node: ScAddr) -> ScAddr:
    search_result = search_non_role_relation_template(src, nrel_node)
    return search_result.get(ScAlias.ELEMENT) if search_result else ScAddr(0)


def get_link_content_data(link: ScAddr) -> ScLinkContentData:
    content_part = client.get_link_content(link)
    return content_part[0].data


def erase_connectors(source: ScAddr, target: ScAddr, *connector_types: ScType) -> bool:
    return client.erase(*get_connectors(source, target, *connector_types))
