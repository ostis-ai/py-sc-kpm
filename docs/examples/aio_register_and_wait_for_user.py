"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""
import asyncio
import logging

from sc_client.models import ScAddr

from asc_kpm import AScAgentClassic, AScModule, AScServer
from sc_kpm import ScResult

logging.basicConfig(level=logging.INFO)


class TestScAgent(AScAgentClassic):
    async def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        return ScResult.OK


async def main() -> None:
    SC_SERVER_URL = "ws://localhost:8090/ws_json"
    server = AScServer(SC_SERVER_URL)
    async with await server.connect():
        module = await AScModule.ainit(await TestScAgent.ainit("sum_action_class"))
        await server.add_modules(module)
        async with await server.register_modules():
            server.serve()


if __name__ == "__main__":
    asyncio.run(main())
