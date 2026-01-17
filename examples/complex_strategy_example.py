import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Logger, Context, SemanticMemory, Backtester
from multiagent_trading.agents.regime_ml import RegimeClassifierAgent
from multiagent_trading.agents.scanner import ScannerAgent
from multiagent_trading.agents.sentiment import SentimentAgent
from multiagent_trading.agents.microstructure import MicrostructureAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.optimizer import PortfolioOptimizerAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.agents.notifications import NotificationAgent
from multiagent_trading.agents.llm_agent import LLMAgent
from multiagent_trading.models.portfolio import PortfolioState

async def main():
    print("Running Advanced Multi-Agent Complex Strategy...")

    config = {
        "execution": {"type": "VWAP"},
        "risk": {"max_exposure": 0.2}
    }

    event_bus = EventBus()
    logger = Logger()

    context = Context(
        portfolio=PortfolioState(initial_value=100000),
        config=config
    )

    # Initialize all agents
    agents = {
        "regime": RegimeClassifierAgent("regime_ml", config, context, event_bus, logger),
        "sentiment": SentimentAgent("sentiment", config, context, event_bus, logger),
        "microstructure": MicrostructureAgent("microstructure", config, context, event_bus, logger),
        "scanner": ScannerAgent("scanner", config, context, event_bus, logger),
        "risk": RiskAgent("risk", config, context, event_bus, logger),
        "optimizer": PortfolioOptimizerAgent("optimizer", config, context, event_bus, logger),
        "supervisor": SupervisorAgent("supervisor", config, context, event_bus, logger),
        "llm": LLMAgent("llm_reasoner", config, context, event_bus, logger),
        "execution": ExecutionAgent("execution", config, context, event_bus, logger),
        "notifications": NotificationAgent("notifier", config, context, event_bus, logger)
    }

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    # Create a complex data feed
    data_feed = []
    for i in range(50):
        # Simulated BTC and ETH prices with some correlation and noise
        btc_price = 40000 + (i * 200) + (1000 * (i % 3))
        eth_price = 2000 + (i * 10) + (50 * (i % 2))
        data_feed.append({
            "BTC/USDT": {"timestamp": i, "close": btc_price},
            "ETH/USDT": {"timestamp": i, "close": eth_price}
        })

    bt = Backtester(orchestrator, data_feed, context)
    results = await bt.run(save_path="complex_backtest_results.json")

    print(f"\nComplex Strategy Finished.")
    print(f"Initial Value: $100,000")
    print(f"Final Value: ${context.portfolio.total_value:,.2f}")
    print(f"Total ROI: {((context.portfolio.total_value / 100000) - 1) * 100:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
