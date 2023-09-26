"""
This code creates agent, executes and confirms the result.
Agent is based on ClassicScAgent and calculates sum of two static arguments.

As you see, SumAgentClassic is more comfortable than ScAgent.
For initialisation, you need only name of action class and event type if it isn't 'add_outgoing_edge'.
"""

import logging

from sc_client.models import ScAddr, ScLinkContentType

from sc_kpm import ScAgentClassic, ScModule, ScResult, ScServer
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.sc_sets import ScStructure
from sc_kpm.utils import create_link, get_link_content_data
from sc_kpm.utils.action_utils import (
    create_action_answer,
    execute_agent,
    finish_action_with_status,
    get_action_answer,
    get_action_arguments,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class SumAgentClassic(ScAgentClassic):
    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("Agent finished %s", "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("Agent began to run")
        arg1_link, arg2_link = get_action_arguments(action_node, 2)
        if not arg1_link or not arg2_link:
            return ScResult.ERROR_INVALID_PARAMS
        arg1_content = get_link_content_data(arg1_link)
        arg2_content = get_link_content_data(arg2_link)
        if not isinstance(arg1_content, int) or not isinstance(arg2_content, int):
            return ScResult.ERROR_INVALID_TYPE
        create_action_answer(action_node, create_link(arg1_content + arg2_content, ScLinkContentType.INT))
        return ScResult.OK


def main():
    server = ScServer("ws://localhost:8090/ws_json")
    with server.start():
        action_class_name = "sum"
        agent = SumAgentClassic(action_class_name)
        module = ScModule(agent)
        server.add_modules(module)
        question, is_successful = execute_agent(
            arguments={
                create_link(2, ScLinkContentType.INT): False,
                create_link(3, ScLinkContentType.INT): False,
            },
            concepts=[CommonIdentifiers.QUESTION, action_class_name],
            wait_time=1,
        )
        assert is_successful
        answer_struct = get_action_answer(question)
        answer_link = ScStructure(set_node=answer_struct).elements_set.pop()
        answer_content = get_link_content_data(answer_link)
        logging.info("Answer received: %s", repr(answer_content))


if __name__ == "__main__":
    main()
