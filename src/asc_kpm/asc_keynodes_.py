"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from logging import Logger, getLogger
from typing import Dict, Optional

from sc_client.constants.sc_types import NODE_CONST_ROLE, ScType
from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr, ScIdtfResolveParams
from sc_client.sc_exceptions import InvalidValueError

Idtf = str


class AScKeynodes:
    """Class which provides the ability to cache the identifier and ScAddr of keynodes stored in the KB."""

    def __init__(self) -> None:
        self._dict: Dict[Idtf, ScAddr] = {}
        self._logger: Logger = getLogger(f"{__name__}.{self.__class__.__name__}")
        self._max_rrel_index: int = 10

    async def get_valid(self, identifier: Idtf) -> ScAddr:
        """Get keynode, cannot be invalid ScAddr(0)"""
        addr = await self.get(identifier)  # pylint: disable=no-value-for-parameter
        if not addr.is_valid():
            self._logger.error("Failed to get ScAddr by %s keynode: ScAddr is invalid", identifier)
            raise InvalidValueError(f"ScAddr of {identifier} is invalid")
        return addr

    async def delete(self, identifier: Idtf) -> bool:
        """Delete keynode from the kb and memory and return boolean status"""
        addr = await self.get_valid(identifier)
        del self._dict[identifier]
        return await asc_client.delete_elements(addr)

    async def get(self, identifier: Idtf) -> ScAddr:
        """Get keynode, can be ScAddr(0)"""
        return await self.resolve(identifier, None)

    async def resolve(self, identifier: Idtf, sc_type: Optional[ScType]) -> ScAddr:
        """Get keynode. If sc_type is valid, an element will be created in the KB"""
        addr = self._dict.get(identifier)
        if addr is None:
            params = ScIdtfResolveParams(idtf=identifier, type=sc_type)
            addr = (await asc_client.resolve_keynodes(params))[0]
            if addr.is_valid():
                self._dict[identifier] = addr
            self._logger.debug("Resolved %s identifier with type %s: %s", repr(identifier), repr(sc_type), repr(addr))
        return addr

    async def rrel_index(self, index: int) -> ScAddr:
        """Get rrel_i node. Max rrel index is 10"""
        if not isinstance(index, int):
            raise TypeError("Index of rrel node must be int")
        if index > self._max_rrel_index:
            raise KeyError(f"You cannot use rrel more than {self._max_rrel_index}")
        return await self.resolve(f"rrel_{index}", NODE_CONST_ROLE)  # pylint: disable=no-value-for-parameter


asc_keynodes = AScKeynodes()
