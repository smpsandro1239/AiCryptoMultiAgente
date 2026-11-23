import asyncio
import unittest

from multiagent_trading.agents.llm_agent import LLMAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.core.logger import Logger
from multiagent_trading.core.orchestrator import Context, EventBus


class TestAgentInteraction(unittest.IsolatedAsyncioTestCase):
    async def test_supervisor_llm_flow(self):
        event_bus = EventBus()
        logger = Logger(level="DEBUG")
        context = Context()

        SupervisorAgent("Supervisor", {}, context, event_bus, logger)
        LLMAgent("LLM", {}, context, event_bus, logger)

        self.reasoning_done = False

        async def on_trade_approved(opportunity):
            self.reasoning_done = True
            self.assertIn("rationale", opportunity)

        event_bus.subscribe("trade_approved", on_trade_approved)
        opportunity = {"symbol": "BTC/USDT", "side": "BUY"}
        await event_bus.publish("risk_assessed", opportunity)
        await asyncio.sleep(0.1)

        self.assertTrue(self.reasoning_done)


if __name__ == "__main__":
    unittest.main()
