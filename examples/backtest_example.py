import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Context, Backtester
from multiagent_trading.core.logger import Logger
from multiagent_trading.core.memory import PersistentSemanticMemory
from multiagent_trading.agents import RegimeAgent, ScannerAgent, RiskAgent, SupervisorAgent, ExecutionAgent, LLMAgent
from multiagent_trading.models.portfolio import PortfolioState
from multiagent_trading.config.loader import load_config
from multiagent_trading.data.loader import load_ohlcv_csv

async def main():
    config = load_config()
    event_bus = EventBus()
    logger = Logger()

    context = Context(
        timestamp=None,
        regime=None,
        portfolio=PortfolioState(),
        market_data=None,
        memory=PersistentSemanticMemory()
    )

    agents = [
        RegimeAgent("regime", config, context, event_bus, logger),
        ScannerAgent("scanner", config, context, event_bus, logger),
        RiskAgent("risk", config, context, event_bus, logger),
        LLMAgent("llm", config, context, event_bus, logger),
        SupervisorAgent("supervisor", config, context, event_bus, logger),
        ExecutionAgent("execution", config, context, event_bus, logger),
    ]

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    data_feed = load_ohlcv_csv("BTCUSDT_1h.csv")
    bt = Backtester(orchestrator, data_feed, context)
    results = await bt.run()

    print("Final PnL History:", results["pnl"])
    print("Final Portfolio Value:", context.portfolio.total_value)

if __name__ == "__main__":
    asyncio.run(main())
