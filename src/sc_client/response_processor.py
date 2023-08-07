from __future__ import annotations

from sc_client.constants import common as c
from sc_client.models import Response, ScAddr, ScEvent, ScLinkContent, ScLinkContentType, ScTemplateResult, ScType
from sc_client.sc_client import ScClient


class BaseResponseProcessor:
    def __init__(self, sc_client: ScClient):
        self.sc_client = sc_client

    def __call__(self, response: Response, *args):
        raise NotImplementedError


class CreateElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        return [ScAddr(addr_value) for addr_value in response.payload]


class CreateElementsBySCsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[bool]:
        return [bool(result) for result in response.payload]


class CheckElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScType]:
        return [ScType(type_value) for type_value in response.payload]


class DeleteElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> bool:
        return response.status


class SetLinkContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> bool:
        return response.status


class GetLinkContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScLinkContent]:
        response_payload = response.payload
        result = []
        for link in response_payload:
            str_type: str = link.get(c.TYPE)
            result.append(ScLinkContent(link.get(c.VALUE), ScLinkContentType[str_type.upper()]))
        return result


class GetLinksByContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.payload
        if response_payload:
            return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response_payload]
        return response_payload


class GetLinksByContentSubstringResponseProcessor(GetLinksByContentResponseProcessor):
    pass


class GetLinksContentsByContentSubstringResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.payload
        return response_payload


class ResolveKeynodesResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        response_payload = response.payload
        if response_payload:
            return [ScAddr(addr_value) for addr_value in response_payload]
        return response  # TODO


class TemplateSearchResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScTemplateResult]:
        result = []
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(c.ALIASES)
            all_addrs = response_payload.get(c.ADDRS)
            for addrs_list in all_addrs:
                addrs = [ScAddr(addr) for addr in addrs_list]
                result.append(ScTemplateResult(addrs, aliases))
        return result


class TemplateGenerateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> ScTemplateResult:
        result = None
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(c.ALIASES)
            addrs_list = response_payload.get(c.ADDRS)
            addrs = [ScAddr(addr) for addr in addrs_list]
            result = ScTemplateResult(addrs, aliases)
        return result


class EventsCreateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *events: ScEvent) -> list[ScEvent]:
        result = []
        for count, event in enumerate(events):
            command_id = response.payload[count]
            sc_event = ScEvent(command_id, event.event_type, event.callback)
            self.sc_client.set_event(sc_event)
            result.append(sc_event)
        return result


class EventsDestroyResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *events: ScEvent) -> bool:
        for event in events:
            self.sc_client.drop_event(event.id)
        return response.status


class ResponseProcessor:
    def __init__(self, sc_client: ScClient):
        self._response_request_mapper = {
            c.ClientCommand.CREATE_ELEMENTS: CreateElementsResponseProcessor(sc_client),
            c.ClientCommand.CREATE_ELEMENTS_BY_SCS: CreateElementsBySCsResponseProcessor(sc_client),
            c.ClientCommand.CHECK_ELEMENTS: CheckElementsResponseProcessor(sc_client),
            c.ClientCommand.DELETE_ELEMENTS: DeleteElementsResponseProcessor(sc_client),
            c.ClientCommand.KEYNODES: ResolveKeynodesResponseProcessor(sc_client),
            c.ClientCommand.GET_LINK_CONTENT: GetLinkContentResponseProcessor(sc_client),
            c.ClientCommand.GET_LINKS_BY_CONTENT: GetLinksByContentResponseProcessor(sc_client),
            c.ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING: GetLinksByContentSubstringResponseProcessor(sc_client),
            c.ClientCommand.GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: (
                GetLinksContentsByContentSubstringResponseProcessor(sc_client)
            ),
            c.ClientCommand.SET_LINK_CONTENTS: SetLinkContentResponseProcessor(sc_client),
            c.ClientCommand.EVENTS_CREATE: EventsCreateResponseProcessor(sc_client),
            c.ClientCommand.EVENTS_DESTROY: EventsDestroyResponseProcessor(sc_client),
            c.ClientCommand.GENERATE_TEMPLATE: TemplateGenerateResponseProcessor(sc_client),
            c.ClientCommand.SEARCH_TEMPLATE: TemplateSearchResponseProcessor(sc_client),
        }

    def run(self, request_type: c.ClientCommand, *args, **kwargs):
        response_processor = self._response_request_mapper.get(request_type)
        return response_processor(*args, **kwargs)
