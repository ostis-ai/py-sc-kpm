"""
This code creates agent, executes and confirms the result.
Agent is based on ClassicScAgent and calculates sum of two static arguments.

As you see, SumAgentClassic is more comfortable than ScAgent.
For initialisation, you need only name of action class and event type if it isn't 'add_outgoing_edge'.
"""
import asyncio
import logging

from sc_client.models import ScAddr, ScLinkContentType

from asc_kpm import AScAgentClassic, AScModule, AScServer
from asc_kpm.asc_sets import AScStructure
from asc_kpm.utils import create_link, get_link_content_data
from asc_kpm.utils.aio_action_utils import (
    create_action_answer,
    execute_agent,
    finish_action_with_status,
    get_action_answer,
    get_action_arguments,
)
from sc_kpm import ScResult
from sc_kpm.identifiers import CommonIdentifiers

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class ASumAgentClassic(AScAgentClassic):
    async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = await self.run(action_element)
        is_successful = result == ScResult.OK
        await finish_action_with_status(action_element, is_successful)
        self.logger.info("Agent finished %s", "successfully" if is_successful else "unsuccessfully")
        return result

    async def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("Agent began to run")
        arg1_link, arg2_link = await get_action_arguments(action_node, 2)
        if not arg1_link or not arg2_link:
            return ScResult.ERROR_INVALID_PARAMS
        arg1_content = await get_link_content_data(arg1_link)
        arg2_content = await get_link_content_data(arg2_link)
        if not isinstance(arg1_content, int) or not isinstance(arg2_content, int):
            return ScResult.ERROR_INVALID_TYPE
        await create_action_answer(action_node, await create_link(arg1_content + arg2_content, ScLinkContentType.INT))
        return ScResult.OK


async def main():
    asc_server = AScServer("ws://localhost:8090/ws_json")
    async with asc_server.start():
        action_class_name = "sum"
        agent = await ASumAgentClassic.ainit(action_class_name)
        module = AScModule(agent)
        await asc_server.add_modules(module)
        question, is_successful = await execute_agent(
            arguments={
                await create_link(2, ScLinkContentType.INT): False,
                await create_link(3, ScLinkContentType.INT): False,
            },
            concepts=[CommonIdentifiers.QUESTION, action_class_name],
            wait_time=1,
        )
        assert is_successful
        answer_struct = await get_action_answer(question)
        answer_link = (await AScStructure(set_node=answer_struct).elements_set).pop()
        answer_content = await get_link_content_data(answer_link)
        logging.info("Answer received: %s", repr(answer_content))


if __name__ == "__main__":
    asyncio.run(main())
