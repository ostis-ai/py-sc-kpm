"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import warnings
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


def create_nodes(*node_types: ScType) -> List[ScAddr]:
    warnings.warn(
        "Common utils 'create_nodes' method is deprecated. Use `generate_nodes` method instead.",
        DeprecationWarning,
    )
    return generate_nodes(*node_types)


def generate_node(node_type: ScType) -> ScAddr:
    return generate_nodes(node_type)[0]


def create_node(node_type: ScType) -> List[ScAddr]:
    warnings.warn(
        "Common utils 'create_node' method is deprecated. Use `generate_node` method instead.",
        DeprecationWarning,
    )
    return generate_nodes(node_type)


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


def create_links(
    *contents: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_type.CONST_NODE_LINK,
) -> List[ScAddr]:
    warnings.warn(
        "Common utils 'create_links' method is deprecated. Use `generate_links` method instead.",
        DeprecationWarning,
    )
    return generate_links(*contents, content_type=content_type, link_type=link_type)


def generate_link(
    content: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_type.CONST_NODE_LINK,
) -> ScAddr:
    return generate_links(content, content_type=content_type, link_type=link_type)[0]


def create_link(
    content: Union[str, int],
    content_type: ScLinkContentType = ScLinkContentType.STRING,
    link_type: ScType = sc_type.CONST_NODE_LINK,
) -> ScAddr:
    warnings.warn(
        "Common utils 'create_link' method is deprecated. Use `generate_link` method instead.",
        DeprecationWarning,
    )
    return generate_link(content, content_type=content_type, link_type=link_type)


def generate_connector(connector_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr:
    return generate_connectors(connector_type, src, trg)[0]


def create_edge(connector_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr:
    warnings.warn(
        "Common utils 'create_edge' method is deprecated. Use `generate_connector` method instead.",
        DeprecationWarning,
    )
    return generate_connector(connector_type, src, trg)


def generate_connectors(connector_type: ScType, src: ScAddr, *targets: ScAddr) -> List[ScAddr]:
    construction = ScConstruction()
    for trg in targets:
        construction.generate_connector(connector_type, src, trg)
    return client.generate_elements(construction)


def create_edges(connector_type: ScType, src: ScAddr, *targets: ScAddr) -> List[ScAddr]:
    warnings.warn(
        "Common utils 'create_edges' method is deprecated. Use `generate_connectors` method instead.",
        DeprecationWarning,
    )
    return generate_connectors(connector_type, src, *targets)


def generate_binary_relation(connector_type: ScType, src: ScAddr, trg: ScAddr, *relations: ScAddr) -> ScAddr:
    construction = ScConstruction()
    construction.generate_connector(connector_type, src, trg, ScAlias.RELATION_ARC)
    for relation in relations:
        construction.generate_connector(sc_type.CONST_PERM_POS_ARC, relation, ScAlias.RELATION_ARC)
    return client.generate_elements(construction)[0]


def create_binary_relation(connector_type: ScType, src: ScAddr, trg: ScAddr, *relations: ScAddr) -> ScAddr:
    warnings.warn(
        "Common utils 'create_binary_relation' method is deprecated. Use `generate_binary_relation` method instead.",
        DeprecationWarning,
    )
    return generate_binary_relation(connector_type, src, trg, *relations)


def generate_role_relation(src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> ScAddr:
    return generate_binary_relation(sc_type.CONST_PERM_POS_ARC, src, trg, *rrel_nodes)


def create_role_relation(src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> ScAddr:
    warnings.warn(
        "Common utils 'create_role_relation' method is deprecated. Use `generate_role_relation` method instead.",
        DeprecationWarning,
    )
    return generate_role_relation(src, trg, *rrel_nodes)


def generate_non_role_relation(src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> ScAddr:
    return generate_binary_relation(sc_type.CONST_COMMON_ARC, src, trg, *nrel_nodes)


def create_norole_relation(src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> ScAddr:
    warnings.warn(
        "Common utils 'create_norole_relation' method is deprecated. Use `generate_non_role_relation` method instead.",
        DeprecationWarning,
    )
    return generate_non_role_relation(src, trg, *nrel_nodes)


def check_connector(connector_type: ScType, source: ScAddr, target: ScAddr) -> bool:
    return bool(search_connectors(source, target, connector_type))


def check_edge(connector_type: ScType, source: ScAddr, target: ScAddr) -> bool:
    warnings.warn(
        "Common utils 'check_edge' method is deprecated. Use `check_connector` method instead.",
        DeprecationWarning,
    )
    return check_connector(connector_type, source, target)


def search_connector(source: ScAddr, target: ScAddr, connector_type: ScType) -> ScAddr:
    connectors = search_connectors(source, target, connector_type)
    return connectors[0] if connectors else ScAddr(0)


def get_edge(source: ScAddr, target: ScAddr, connector_type: ScType) -> ScAddr:
    warnings.warn(
        "Common utils 'get_edge' method is deprecated. Use `search_connector` method instead.",
        DeprecationWarning,
    )
    return search_connector(source, target, connector_type)


def search_connectors(source: ScAddr, target: ScAddr, *connector_types: ScType) -> List[ScAddr]:
    result_connectors = []
    for connector_type in connector_types:
        templ = ScTemplate()
        templ.triple(source, connector_type, target)
        results = client.search_by_template(templ)
        result_connectors.extend(result[1] for result in results)
    return result_connectors


def get_edges(source: ScAddr, target: ScAddr, *connector_types: ScType) -> List[ScAddr]:
    warnings.warn(
        "Common utils 'get_edges' method is deprecated. Use `search_connectors` method instead.",
        DeprecationWarning,
    )
    return search_connectors(source, target, *connector_types)


def get_element_system_identifier(addr: ScAddr) -> Idtf:
    nrel_system_idtf = ScKeynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER]

    templ = ScTemplate()
    templ.quintuple(
        addr,
        sc_type.VAR_COMMON_ARC,
        sc_type.VAR_NODE_LINK >> ScAlias.LINK,
        sc_type.VAR_PERM_POS_ARC,
        nrel_system_idtf,
    )
    result = client.search_by_template(templ)
    if result:
        return get_link_content_data(result[0].get(ScAlias.LINK))
    return ""


def get_system_idtf(addr: ScAddr) -> Idtf:
    warnings.warn(
        "Common utils 'get_system_idtf' method is deprecated. Use `get_element_system_identifier` method instead.",
        DeprecationWarning,
    )
    return get_element_system_identifier(addr)


def _search_relation_template(src: ScAddr, rel_node: ScAddr, rel_type: ScType) -> Optional[ScTemplateResult]:
    template = ScTemplate()
    template.quintuple(
        src,
        rel_type >> ScAlias.RELATION_ARC,
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


def search_norole_relation_template(src: ScAddr, nrel_node: ScAddr) -> Optional[ScTemplateResult]:
    warnings.warn(
        "Common utils 'search_norole_relation_template' method is deprecated."
        "Use `search_non_role_relation_template` method instead.",
        DeprecationWarning,
    )
    return search_non_role_relation_template(src, nrel_node)


def search_element_by_role_relation(src: ScAddr, rrel_node: ScAddr) -> ScAddr:
    search_result = search_role_relation_template(src, rrel_node)
    return search_result.get(ScAlias.ELEMENT) if search_result else ScAddr(0)


def get_element_by_role_relation(src: ScAddr, rrel_node: ScAddr) -> ScAddr:
    warnings.warn(
        "Common utils 'get_element_by_role_relation' method is deprecated."
        "Use `search_element_by_role_relation` method instead.",
        DeprecationWarning,
    )
    return search_element_by_role_relation(src, rrel_node)


def search_element_by_non_role_relation(src: ScAddr, nrel_node: ScAddr) -> ScAddr:
    search_result = search_non_role_relation_template(src, nrel_node)
    return search_result.get(ScAlias.ELEMENT) if search_result else ScAddr(0)


def get_element_by_norole_relation(src: ScAddr, nrel_node: ScAddr) -> ScAddr:
    warnings.warn(
        "Common utils 'get_element_by_norole_relation' method is deprecated."
        "Use `search_element_by_non_role_relation` method instead.",
        DeprecationWarning,
    )
    return search_element_by_non_role_relation(src, nrel_node)


def get_link_content_data(link: ScAddr) -> ScLinkContentData:
    content_part = client.get_link_content(link)
    return content_part[0].data


def erase_connectors(source: ScAddr, target: ScAddr, *connector_types: ScType) -> bool:
    return client.erase_elements(*search_connectors(source, target, *connector_types))


def delete_edges(source: ScAddr, target: ScAddr, *connector_types: ScType) -> bool:
    warnings.warn(
        "Common utils 'delete_edges' method is deprecated. Use `erase_connectors` method instead.",
        DeprecationWarning,
    )
    return erase_connectors(source, target, *connector_types)
