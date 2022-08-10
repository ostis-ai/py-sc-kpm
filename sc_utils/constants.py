"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from enum import Enum

COMMON_WAIT_TIME = 5
RREL_PREFIX = "rrel_"


class ScAlias(Enum):
    ACTION_NODE = "_action_node"
    RELATION_EDGE = "_relation_edge"
    RELATION_NODE = "_relation_node"
    ELEMENT = "_element"
    COMMON_EDGE = "_common_edge"
    ACCESS_EDGE = "_access_edge"
    NEXT_EDGE = "_next_edge"
    NODE = "_node"
    LINK = "_link"
    SYS_IDTF = "_sys_idtf"


class FileType(Enum):
    RDF = "rdf"
    XML = "xml"
