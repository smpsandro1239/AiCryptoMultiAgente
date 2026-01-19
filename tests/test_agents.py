import unittest
import asyncio
from multiagent_trading.core.orchestrator import EventBus, Context, Orchestrator
from multiagent_trading.core.logger import Logger
from multiagent_trading.agents.llm_agent import LLMAgent
from multiagent_trading.agents.supervisor import SupervisorAgent

class TestAgentInteraction(unittest.IsolatedAsyncioTestCase):
    async def test_supervisor_llm_flow(self):
        eb = EventBus()
        logger = Logger(level="DEBUG")
        ctx = Context()

        supervisor = SupervisorAgent("Supervisor", {}, ctx, eb, logger)
        llm = LLMAgent("LLM", {}, ctx, eb, logger)

        # Test flag
        self.reasoning_done = False

        async def on_trade_approved(opp):
            self.reasoning_done = True
            self.assertIn("rationale", opp)

        eb.subscribe("trade_approved", on_trade_approved)

        opp = {"symbol": "BTC/USDT", "side": "BUY"}
        await eb.publish("risk_assessed", opp)

        # Give some time for async tasks
        await asyncio.sleep(0.1)

        self.assertTrue(self.reasoning_done)

if __name__ == "__main__":
    unittest.main()
