"""
This code creates agent, executes and confirms the result.
Agent is based on ScAgent and calculates sum of two static arguments.

As you see, ScAgent is less comfortable than SumAgentClassic, but you can customize it in more details.
"""

import logging
from typing import Union

from sc_kpm import ScAddr, ScAgent, ScEventType, ScLinkContentType, ScModule, ScResult, ScServer
from sc_kpm.identifiers import CommonIdentifiers, QuestionStatus
from sc_kpm.sc_keynodes import Idtf
from sc_kpm.utils import create_link, get_link_content
from sc_kpm.utils.action_utils import (
    check_action_class,
    create_action_answer,
    execute_agent,
    finish_action_with_status,
    get_action_answer,
    get_action_arguments,
)
from sc_kpm.utils.retrieve_utils import get_set_elements

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class SumAgent(ScAgent):
    def __init__(self, event_class: Union[Idtf, ScAddr], event_type: ScEventType, action_class_name: ScAddr):
        super().__init__(event_class, event_type)
        self._action_class_name = action_class_name
        self._logger = logging.getLogger(f"{self.__module__}:{self.__class__.__name__}")

    def on_event(self, init_element: ScAddr, init_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self._logger.info("Agent was called")
        if not check_action_class(self._action_class_name, action_element):
            return ScResult.SKIP
        self._logger.info("Agent was confirmed")
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self._logger.info("Agent finished %s", "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self._logger.info("Agent began to run")
        arg1_link, arg2_link = get_action_arguments(action_node, 2)
        if not arg1_link or not arg2_link:
            return ScResult.ERROR_INVALID_PARAMS
        arg1_content = get_link_content(arg1_link)
        arg2_content = get_link_content(arg2_link)
        if not isinstance(arg1_content, int) or not isinstance(arg2_content, int):
            return ScResult.ERROR_INVALID_TYPE
        create_action_answer(action_node, create_link(arg1_content + arg2_content, ScLinkContentType.INT))
        return ScResult.OK


def main():
    server = ScServer("ws://localhost:8090/ws_json")
    with server.connect():
        ACTION_CLASS_NAME = "sum"
        agent = SumAgent(
            QuestionStatus.QUESTION_INITIATED.value,
            ScEventType.ADD_OUTGOING_EDGE,
            ACTION_CLASS_NAME,
        )
        module = ScModule(agent)
        server.add_modules(module)
        with server.register_modules():
            question, is_successful = execute_agent(
                arguments={
                    create_link(2, ScLinkContentType.INT): False,
                    create_link(3, ScLinkContentType.INT): False,
                },
                concepts=[CommonIdentifiers.QUESTION.value, ACTION_CLASS_NAME],
                wait_time=1,
            )
            assert is_successful
            answer_struct = get_action_answer(question)
            answer_link = get_set_elements(answer_struct)[0]
            answer_content = get_link_content(answer_link)
            logging.info("Answer received: %s", repr(answer_content))


if __name__ == "__main__":
    main()
