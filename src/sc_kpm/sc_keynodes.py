"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from __future__ import annotations

from sc_client import client
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScIdtfResolveParams

Idtf = str


class ScKeynodes(dict):
    _instance = {}

    def __new__(cls) -> ScKeynodes:
        if not isinstance(cls._instance, cls):
            cls._instance = dict.__new__(cls)
        return cls._instance

    def __getitem__(self, identifier: Idtf) -> ScAddr:
        addr = self._instance.get(identifier)
        if addr is None:
            params = ScIdtfResolveParams(idtf=identifier, type=None)
            addr = client.resolve_keynodes(params)[0]
            self._instance[identifier] = addr
        return addr

    def resolve(self, identifier: Idtf, sc_type: ScType = None) -> ScAddr:
        addr = self._instance.get(identifier)
        if addr is None:
            params = ScIdtfResolveParams(idtf=identifier, type=sc_type)
            addr = client.resolve_keynodes(params)[0]
            self._instance[identifier] = addr
        return addr
