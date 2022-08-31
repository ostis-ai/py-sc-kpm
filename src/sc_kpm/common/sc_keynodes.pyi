"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr

class ScKeynodes(dict):
    _instance: ScKeynodes

    def __new__(cls) -> ScKeynodes: ...
    def __getitem__(self, identifier: str) -> ScAddr: ...
    def resolve(self, identifier: str, sc_type: ScType = None) -> ScAddr: ...
