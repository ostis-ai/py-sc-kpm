"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from typing import List

from sc_client import client
from sc_client.constants import sc_types
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScConstruction, ScIdtfResolveParams, ScLinkContent, ScLinkContentType

from sc_common.identifiers import CommonIdentifiers
from sc_common.sc_keynodes import ScKeynodes
from sc_utils.constants import ScAlias


def generate_nodes(*node_types: ScType) -> List[ScAddr]:
    construction = ScConstruction()
    for node_type in node_types:
        construction.create_node(node_type)
    return client.create_elements(construction)


def generate_node(node_type: ScType) -> ScAddr:
    return generate_nodes(node_type)[0]


def generate_node_with_idtf(node_type: ScType, idtf: str) -> ScAddr:
    params = ScIdtfResolveParams(idtf=idtf, type=node_type)
    return client.resolve_keynodes(params)[0]


def generate_links(*contents: str) -> List[ScAddr]:
    construction = ScConstruction()
    for content in contents:
        link_content = ScLinkContent(content, ScLinkContentType.STRING.value)
        construction.create_link(sc_types.LINK, link_content)
    return client.create_elements(construction)


def generate_link(content: str) -> ScAddr:
    return generate_links(content)[0]


def generate_edge(src: ScAddr, trg: ScAddr, edge_type: ScType) -> ScAddr:
    construction = ScConstruction()
    construction.create_edge(edge_type, src, trg)
    return client.create_elements(construction)[0]


def generate_binary_relation(src: ScAddr, edge_type: ScType, trg: ScAddr, *relations: ScAddr) -> ScAddr:
    construction = ScConstruction()
    construction.create_edge(edge_type, src, trg, ScAlias.RELATION_EDGE.value)
    for relation in relations:
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, relation, ScAlias.RELATION_EDGE.value)
    return client.create_elements(construction)[0]


def wrap_in_oriented_set(set_node: ScAddr, *elements: ScAddr) -> None:
    keynodes = ScKeynodes()
    if len(elements) > 0:
        rrel_one = keynodes[CommonIdentifiers.RREL_ONE.value]
        nrel_sequence = keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE.value]
        curr_edge = generate_binary_relation(set_node, sc_types.EDGE_ACCESS_CONST_POS_PERM, elements.pop(0), rrel_one)
        while elements:
            next_element = elements.pop(0)
            next_edge = generate_edge(set_node, next_element, sc_types.EDGE_ACCESS_CONST_POS_PERM)
            generate_binary_relation(curr_edge, sc_types.EDGE_D_COMMON_CONST, next_edge, nrel_sequence)
            curr_edge = next_edge


def generate_oriented_set(*elements: ScAddr) -> ScAddr:
    set_node = generate_node(sc_types.NODE_CONST)
    wrap_in_oriented_set(set_node, *elements)
    return set_node


def wrap_in_structure(struct_node: ScAddr, *elements: ScAddr) -> None:
    for elem in elements:
        generate_edge(struct_node, elem, sc_types.EDGE_ACCESS_CONST_POS_PERM)


def generate_structure(*elements: ScAddr) -> ScAddr:
    struct_node = generate_node(sc_types.NODE_CONST_STRUCT)
    for elem in elements:
        generate_edge(struct_node, elem, sc_types.EDGE_ACCESS_CONST_POS_PERM)
    return struct_node
