from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple, Union

from sc_client.exceptions import InvalidTypeError
from sc_client.models.sc_addr import ScAddr
from sc_client.models.sc_type import ScType

ScTemplateValueItem = Union[ScAddr, ScType, str]
ScTemplateAliasedItem = Tuple[Union[ScAddr, ScType], str]
ScTemplateParam = Union[ScTemplateValueItem, ScTemplateAliasedItem]
ScTemplateParams = Dict[str, Union[ScAddr, str]]
ScTemplateIdtf = str


class ScTemplateValue:
    value: ScTemplateValueItem
    alias: Optional[str] = None

    def __init__(self, param: ScTemplateParam):
        if isinstance(param, tuple):
            param, alias = param
            if not isinstance(alias, str):
                raise InvalidTypeError("Alias must be str")
            if not isinstance(param, (ScAddr, ScType)):
                raise InvalidTypeError("Value with alias must be ScAddr")
            self.alias = alias
        if isinstance(param, ScType) and param.is_const():
            raise InvalidTypeError("You should to use variable types in template")
        self.value = param


@dataclass
class ScTemplateTriple:
    src: ScTemplateValue
    edge: ScTemplateValue
    trg: ScTemplateValue

    def __init__(self, src: ScTemplateParam, edge: ScTemplateParam, trg: ScTemplateParam):
        self.src = ScTemplateValue(src)
        self.edge = ScTemplateValue(edge)
        self.trg = ScTemplateValue(trg)


class ScTemplate:
    def __init__(self) -> None:
        self.triple_list: List[ScTemplateTriple] = []

    def triple(
        self,
        src: ScTemplateParam,
        edge: ScTemplateParam,
        trg: ScTemplateParam,
    ) -> None:
        self.triple_list.append(ScTemplateTriple(src, edge, trg))

    def triple_with_relation(
        self,
        src: ScTemplateParam,
        edge: ScTemplateParam,
        trg: ScTemplateParam,
        edge2: ScTemplateParam,
        src2: ScTemplateParam,
    ) -> None:
        if not isinstance(edge, (tuple, list)):  # TODO: remove list support in version 0.3.0
            edge_alias = f"edge_1_{len(self.triple_list)}"
            edge = (edge, edge_alias)
        self.triple(src, edge, trg)
        self.triple(src2, edge2, edge[1])


class ScTemplateResult:
    addrs_iter: Iterator[ScAddr]

    def __init__(self, addrs: List[ScAddr], aliases: Dict[str, int]) -> None:
        self.addrs = addrs
        self.aliases = aliases

    def __len__(self) -> int:
        return len(self.addrs)

    def get(self, alias_or_index: Union[str, int]) -> ScAddr:
        """Get ScAddr by alias or index in the template result"""
        if isinstance(alias_or_index, str):
            return self.addrs[self.aliases[alias_or_index]]
        return self.addrs[alias_or_index]

    def __getitem__(self, index: int) -> ScAddr:
        """Get ScAddr by index in the template result"""
        return self.addrs[index]

    def __iter__(self):
        """Iterate by triples"""
        self.addrs_iter = iter(self.addrs)
        return self

    def __next__(self) -> Tuple[ScAddr, ScAddr, ScAddr]:
        return next(self.addrs_iter), next(self.addrs_iter), next(self.addrs_iter)
