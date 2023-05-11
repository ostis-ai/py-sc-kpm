from sc_client.client import check_elements
from sc_client.constants import ScType, sc_types
from sc_client.constants.exceptions import InvalidTypeError
from sc_client.models import ScAddr

from sc_kpm.sc_sets.sc_set import ScSet


class ScStructure(ScSet):
    """
    ScStructure is a class for handling structure construction in kb.

    It has main set_node with type NODE_CONST_STRUCT and edged elements.
    """

    def __init__(self, *elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None) -> None:
        if set_node_type is None:
            set_node_type = sc_types.NODE_CONST_STRUCT
        if set_node is not None:
            set_node_type = check_elements(set_node)[0]
        if not set_node_type.is_struct():
            raise InvalidTypeError
        super().__init__(*elements, set_node=set_node, set_node_type=set_node_type)
