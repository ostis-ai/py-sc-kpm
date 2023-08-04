from sc_client.client.payload_factory import PayloadFactory
from sc_client.client.response_processor import ResponseProcessor
from sc_client.client.sc_client import ScClient
from sc_client.constants.common import ERRORS, MESSAGE, REF, ClientCommand, RequestType
from sc_client.exceptions import ServerError


class Executor:
    def __init__(self, sc_client: ScClient):
        self.payload_factory = PayloadFactory()
        self.response_processor = ResponseProcessor(sc_client)
        self.sc_client = sc_client
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
        response = self.sc_client.send_message(self._executor_mapper.get(command_type), payload)
        if response.get(ERRORS):
            error_msgs = []
            errors = response.get(ERRORS)
            if isinstance(errors, str):
                error_msgs.append(errors)
            else:
                for error in errors:
                    payload_part = "\nPayload: " + str(payload[int(error.get(REF))]) if error.get(REF) else ""
                    error_msgs.append(error.get(MESSAGE) + payload_part)
            error_msgs = "\n".join(error_msgs)
            raise ServerError(error_msgs)
        return self.response_processor.run(command_type, response, *args)
