import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Logger, Context, SemanticMemory, Backtester
from multiagent_trading.agents.regime_ml import RegimeClassifierAgent
from multiagent_trading.agents.scanner import ScannerAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.optimizer import PortfolioOptimizerAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.models.portfolio import PortfolioState

async def main():
    config = {"execution": {"type": "VWAP"}}
    event_bus = EventBus()
    logger = Logger()

    context = Context(
        portfolio=PortfolioState(initial_value=10000),
        config=config
    )

    agents = {
        "regime_ml": RegimeClassifierAgent("regime_ml", config, context, event_bus, logger),
        "scanner": ScannerAgent("scanner", config, context, event_bus, logger),
        "risk": RiskAgent("risk", config, context, event_bus, logger),
        "optimizer": PortfolioOptimizerAgent("optimizer", config, context, event_bus, logger),
        "supervisor": SupervisorAgent("supervisor", config, context, event_bus, logger),
        "execution": ExecutionAgent("execution", config, context, event_bus, logger),
    }

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    # Generate enough data to train the ML model
    data_feed = []
    for i in range(30):
        price = 100 + i + (5 * (i % 2)) # Some fake trend and noise
        data_feed.append({"BTC/USDT": {"timestamp": i, "close": price}})

    bt = Backtester(orchestrator, data_feed, context)
    results = await bt.run()

    print("\n--- ML Regime Classification Example Results ---")
    print(f"Final Portfolio Value: {context.portfolio.total_value}")
    print(f"Final Predicted Regime: {context.regime}")

if __name__ == "__main__":
    asyncio.run(main())
