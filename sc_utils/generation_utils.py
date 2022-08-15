from sc_client.constants import sc_types
from sc_client.models import ScAddr

from sc_common.identifiers import CommonIdentifiers
from sc_common.sc_keynodes import ScKeynodes
from sc_utils.common_utils import generate_role_relation, generate_edge, generate_norole_relation, generate_node


def wrap_in_oriented_set(set_node: ScAddr, start_element: ScAddr, *elements: ScAddr) -> None:
    keynodes = ScKeynodes()
    rrel_one = keynodes[CommonIdentifiers.RREL_ONE.value]
    nrel_sequence = keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE.value]
    curr_edge = generate_role_relation(set_node, start_element, rrel_one)
    for next_element in elements:
        next_edge = generate_edge(set_node, sc_types.EDGE_ACCESS_CONST_POS_PERM, next_element)
        generate_norole_relation(curr_edge, next_edge, nrel_sequence)
        curr_edge = next_edge


def generate_oriented_set(*elements: ScAddr) -> ScAddr:
    set_node = generate_node(sc_types.NODE_CONST)
    wrap_in_oriented_set(set_node, *elements)
    return set_node


def wrap_in_structure(struct_node: ScAddr, *elements: ScAddr) -> None:
    for elem in elements:
        generate_edge(struct_node, sc_types.EDGE_ACCESS_CONST_POS_PERM, elem)


def generate_structure(*elements: ScAddr) -> ScAddr:
    struct_node = generate_node(sc_types.NODE_CONST_STRUCT)
    for elem in elements:
        generate_edge(struct_node, sc_types.EDGE_ACCESS_CONST_POS_PERM, elem)
    return struct_node
