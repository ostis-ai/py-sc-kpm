"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScTemplate

from sc_common.identifiers import CommonIdentifiers
from sc_common.sc_keynodes import ScKeynodes
from sc_utils.constants import ScAlias


def template_next_element_of_oriented_set(set_node: ScAddr, curr_element_edge: ScAddr) -> ScTemplate:
    keynodes = ScKeynodes()
    templ = ScTemplate()
    templ.triple_with_relation(
        curr_element_edge,
        sc_types.EDGE_D_COMMON_VAR,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAlias.ACCESS_EDGE.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes[CommonIdentifiers.NREL_BASIC_SEQUENCE.value],
    )
    templ.triple(set_node, ScAlias.ACCESS_EDGE.value, [sc_types.UNKNOWN, ScAlias.ELEMENT.value])
    return templ
