import unittest

from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.agents.llm_agent import LLMAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.scanner import ScannerAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.core.logger import Logger
from multiagent_trading.core.orchestrator import Context, EventBus


class InMemoryStore:
    def __init__(self):
        self.items = []

    def add(self, key, value):
        self.items.append((key, value))


class TestAgentInteraction(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.event_bus = EventBus()
        self.logger = Logger(level="DEBUG")
        self.context = Context(memory=InMemoryStore())
        self.risk = RiskAgent("Risk", {"initial_capital": 10_000}, self.context, self.event_bus, self.logger)
        self.supervisor = SupervisorAgent("Supervisor", {}, self.context, self.event_bus, self.logger)
        self.llm = LLMAgent("LLM", {}, self.context, self.event_bus, self.logger)
        self.execution = ExecutionAgent("Execution", {}, self.context, self.event_bus, self.logger)
        self.scanner = ScannerAgent("Scanner", {}, self.context, self.event_bus, self.logger)
        self.fills = []
        self.rejections = []
        self.event_bus.subscribe("paper_fill", self.fills.append)
        self.event_bus.subscribe("trade_rejected", self.rejections.append)

    async def test_only_risk_approved_opportunity_reaches_paper_execution(self):
        opportunity = {
            "symbol": "BTC/USDT",
            "side": "BUY",
            "entry_price": 100.0,
            "stop_price": 90.0,
            "risk_ok": False,
        }
        await self.event_bus.publish("opportunity_found", opportunity)

        self.assertEqual(len(self.fills), 1)
        self.assertEqual(self.fills[0]["execution_mode"], "paper")
        self.assertEqual(self.fills[0]["order_status"], "filled")
        self.assertGreater(self.context.portfolio.positions["BTC/USDT"].quantity, 0)
        self.assertEqual(len(self.context.memory.items), 1)
        self.assertTrue(opportunity["risk_decision"]["approved"])

    async def test_scanner_forwards_real_market_prices_into_risk_gate(self):
        await self.event_bus.publish("market_update", {
            "symbol": "ETH/USDT", "close": 50.0, "stop_price": 45.0,
        })
        self.assertEqual(len(self.fills), 1)
        self.assertEqual(self.fills[0]["symbol"], "ETH/USDT")

    async def test_missing_stop_is_rejected_and_never_executed(self):
        opportunity = {"symbol": "BTC/USDT", "side": "BUY", "entry_price": 100.0}
        await self.event_bus.publish("opportunity_found", opportunity)

        self.assertEqual(self.fills, [])
        self.assertEqual(len(self.rejections), 1)
        self.assertFalse(opportunity["risk_decision"]["approved"])
        self.assertEqual(self.context.portfolio.positions, {})

    async def test_duplicate_order_identifier_is_rejected(self):
        opportunity = {
            "order_id": "order-unique-1",
            "symbol": "BTC/USDT",
            "side": "BUY",
            "entry_price": 100.0,
            "stop_price": 90.0,
        }
        await self.event_bus.publish("opportunity_found", opportunity)
        await self.event_bus.publish("opportunity_found", opportunity)

        self.assertEqual(len(self.fills), 1)
        self.assertTrue(any("Duplicate" in item.get("rejection_reason", "") for item in self.rejections))


if __name__ == "__main__":
    unittest.main()
