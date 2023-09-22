from __future__ import annotations

from sc_client import ScType
from sc_client.constants import sc_types
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr
from sc_client.sc_exceptions import InvalidTypeError

from aio_sc_kpm.sc_sets.asc_set import AScSet


class AScStructure(AScSet):
    """
    ScStructure is a class for handling structure construction in kb.

    It has main set_node with type NODE_CONST_STRUCT and edged elements.
    """

    @classmethod
    async def create(cls, *elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None) -> AScStructure:
        if set_node_type is None:
            set_node_type = sc_types.NODE_CONST_STRUCT
        if set_node is not None:
            set_node_type = asc_client.check_elements(set_node)[0]
        if not set_node_type.is_struct():
            raise InvalidTypeError
        return await super().create(*elements, set_node=set_node, set_node_type=set_node_type)
