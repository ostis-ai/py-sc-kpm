from sc_client.client import get_elements_types
from sc_client.constants import ScType, sc_type
from sc_client.constants.exceptions import InvalidTypeError
from sc_client.models import ScAddr

from sc_kpm.sc_sets.sc_set import ScSet


class ScStructure(ScSet):
    """
    ScStructure is a class for handling structure construction in kb.

    It has main set_node with type CONST_NODE_STRUCTURE and elements.
    """

    def __init__(self, *elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None) -> None:
        if set_node_type is None:
            set_node_type = sc_type.CONST_NODE_STRUCTURE
        if set_node is not None:
            set_node_type = get_elements_types(set_node)[0]
        if not set_node_type.is_structure():
            raise InvalidTypeError
        super().__init__(*elements, set_node=set_node, set_node_type=set_node_type)
