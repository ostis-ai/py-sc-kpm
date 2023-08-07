from __future__ import annotations

from sc_client.constants import common
from sc_client.constants.common import MESSAGE, REF, ClientCommand, RequestType
from sc_client.constants.config import SERVER_RECONNECT_RETRIES, SERVER_RECONNECT_RETRY_DELAY
from sc_client.exceptions import InvalidTypeError, ServerError
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    SCsText,
    ScTemplate,
    ScTemplateIdtf,
    ScTemplateParams,
    ScTemplateResult,
    ScType,
)
from sc_client.models.sc_construction import ScLinkContentData
from sc_client.sc_client.payload_factory import PayloadFactory
from sc_client.sc_client.response_processor import ResponseProcessor
from sc_client.sc_client.sc_connection import ScConnection


class ScClient:
    def __init__(self):
        self.sc_connection = ScConnection()
        self.payload_factory = PayloadFactory()
        self.response_processor = ResponseProcessor(self.sc_connection)
        self._executor_mapper = {
            ClientCommand.CREATE_ELEMENTS: RequestType.CREATE_ELEMENTS,
            ClientCommand.CREATE_ELEMENTS_BY_SCS: RequestType.CREATE_ELEMENTS_BY_SCS,
            ClientCommand.CHECK_ELEMENTS: RequestType.CHECK_ELEMENTS,
            ClientCommand.DELETE_ELEMENTS: RequestType.DELETE_ELEMENTS,
            ClientCommand.KEYNODES: RequestType.KEYNODES,
            ClientCommand.GET_LINK_CONTENT: RequestType.CONTENT,
            ClientCommand.GET_LINKS_BY_CONTENT: RequestType.CONTENT,
            ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING: RequestType.CONTENT,
            ClientCommand.GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: RequestType.CONTENT,
            ClientCommand.SET_LINK_CONTENTS: RequestType.CONTENT,
            ClientCommand.EVENTS_CREATE: RequestType.EVENTS,
            ClientCommand.EVENTS_DESTROY: RequestType.EVENTS,
            ClientCommand.GENERATE_TEMPLATE: RequestType.GENERATE_TEMPLATE,
            ClientCommand.SEARCH_TEMPLATE: RequestType.SEARCH_TEMPLATE,
        }

    def run(self, command_type: ClientCommand, *args):
        payload = self.payload_factory.run(command_type, *args)
        response = self.sc_connection.send_message(self._executor_mapper.get(command_type), payload)
        if response.errors:
            error_msgs = []
            errors = response.errors
            if isinstance(errors, str):
                error_msgs.append(errors)
            else:
                for error in errors:
                    payload_part = "\nPayload: " + str(payload[int(error.get(REF))]) if error.get(REF) else ""
                    error_msgs.append(error.get(MESSAGE) + payload_part)
            error_msgs = "\n".join(error_msgs)
            raise ServerError(error_msgs)
        return self.response_processor.run(command_type, response, *args)

    def connect(self, url: str) -> None:
        self.sc_connection.set_connection(url)

    def is_connected(self) -> bool:
        return self.sc_connection.is_connected()

    def disconnect(self) -> None:
        self.sc_connection.close_connection()

    def set_error_handler(self, callback) -> None:
        self.sc_connection.set_error_handler(callback)

    def set_reconnect_handler(self, **reconnect_kwargs) -> None:
        self.sc_connection.set_reconnect_handler(
            reconnect_kwargs.get("reconnect_handler", self.sc_connection.default_reconnect_handler),
            reconnect_kwargs.get("post_reconnect_handler"),
            reconnect_kwargs.get("reconnect_retries", SERVER_RECONNECT_RETRIES),
            reconnect_kwargs.get("reconnect_retry_delay", SERVER_RECONNECT_RETRY_DELAY),
        )

    def check_elements(self, *addrs: ScAddr) -> list[ScType]:
        return self.run(common.ClientCommand.CHECK_ELEMENTS, *addrs)

    def create_elements(self, constr: ScConstruction) -> list[ScAddr]:
        return self.run(common.ClientCommand.CREATE_ELEMENTS, constr)

    def create_elements_by_scs(self, text: SCsText) -> list[bool]:
        return self.run(common.ClientCommand.CREATE_ELEMENTS_BY_SCS, text)

    def delete_elements(self, *addrs: ScAddr) -> bool:
        return self.run(common.ClientCommand.DELETE_ELEMENTS, *addrs)

    def set_link_contents(self, *contents: ScLinkContent) -> bool:
        return self.run(common.ClientCommand.SET_LINK_CONTENTS, *contents)

    def get_link_content(self, *addr: ScAddr) -> list[ScLinkContent]:
        return self.run(common.ClientCommand.GET_LINK_CONTENT, *addr)

    def get_links_by_content(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self.run(common.ClientCommand.GET_LINKS_BY_CONTENT, *contents)

    def get_links_by_content_substring(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self.run(common.ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING, *contents)

    def get_links_contents_by_content_substring(
        self, *contents: ScLinkContent | ScLinkContentData
    ) -> list[list[ScAddr]]:
        return self.run(common.ClientCommand.GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING, *contents)

    def resolve_keynodes(self, *params: ScIdtfResolveParams) -> list[ScAddr]:
        return self.run(common.ClientCommand.KEYNODES, *params)

    def template_search(
        self, template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
    ) -> list[ScTemplateResult]:
        return self.run(common.ClientCommand.SEARCH_TEMPLATE, template, params)

    def template_generate(
        self, template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
    ) -> ScTemplateResult:
        return self.run(common.ClientCommand.GENERATE_TEMPLATE, template, params)

    def events_create(self, *events: ScEventParams) -> list[ScEvent]:
        return self.run(common.ClientCommand.EVENTS_CREATE, *events)

    def events_destroy(self, *events: ScEvent) -> bool:
        return self.run(common.ClientCommand.EVENTS_DESTROY, *events)

    def is_event_valid(self, event: ScEvent) -> bool:
        if not isinstance(event, ScEvent):
            raise InvalidTypeError("expected object types: ScEvent")
        return bool(self.sc_connection.get_event(event.id))
