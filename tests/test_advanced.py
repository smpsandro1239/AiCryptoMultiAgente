import unittest
import asyncio
from multiagent_trading.core.strategy import StrategyManager
from multiagent_trading.agents.microstructure import MicrostructureAgent
from multiagent_trading.core.orchestrator import EventBus, Logger, Context, SemanticMemory

class TestAdvancedFeatures(unittest.TestCase):
    def test_strategy_manager(self):
        sm = StrategyManager(strategies_dir="test_strategies")
        config = {"scanner": {"period": 14}}
        sm.save_strategy("trend_follower", config)
        self.assertIn("trend_follower", sm.list_strategies())
        self.assertEqual(sm.get_strategy("trend_follower"), config)

        # Cleanup
        import shutil
        shutil.rmtree("test_strategies")

    def test_microstructure_agent(self):
        bus = EventBus()
        logger = Logger()
        context = Context()
        agent = MicrostructureAgent("ms_agent", {}, context, bus, logger)

        received = []
        async def callback(data):
            received.append(data)
        bus.subscribe("microstructure_update", callback)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(agent.on_market_update({"BTC/USDT": {"close": 40000}}))

        self.assertEqual(len(received), 1)
        self.assertTrue(context.microstructure["BTC/USDT"]["liquidity_ok"])

if __name__ == "__main__":
    unittest.main()
