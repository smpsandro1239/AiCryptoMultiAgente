import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Logger, Context, SemanticMemory, Backtester
from multiagent_trading.agents.regime import RegimeAgent
from multiagent_trading.agents.scanner import ScannerAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.optimizer import PortfolioOptimizerAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.models.portfolio import PortfolioState
from multiagent_trading.config.loader import load_config
from multiagent_trading.analytics.reporting import generate_report, plot_performance

async def main():
    config = load_config()
    event_bus = EventBus()
    logger = Logger()

    context = Context(
        timestamp=None,
        regime=None,
        portfolio=PortfolioState(initial_value=10000),
        market_data={},
        memory=SemanticMemory(),
        config=config
    )

    agents = {
        "regime": RegimeAgent("regime", config, context, event_bus, logger),
        "scanner": ScannerAgent("scanner", config, context, event_bus, logger),
        "risk": RiskAgent("risk", config, context, event_bus, logger),
        "optimizer": PortfolioOptimizerAgent("optimizer", config, context, event_bus, logger),
        "supervisor": SupervisorAgent("supervisor", config, context, event_bus, logger),
        "execution": ExecutionAgent("execution", config, context, event_bus, logger),
    }

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    # Multi-symbol mock data
    data_feed = [
        {
            "BTC/USDT": {"timestamp": 1, "close": 40000},
            "ETH/USDT": {"timestamp": 1, "close": 2000}
        },
        {
            "BTC/USDT": {"timestamp": 2, "close": 40500},
            "ETH/USDT": {"timestamp": 2, "close": 2100}
        },
        {
            "BTC/USDT": {"timestamp": 3, "close": 38000}, # Significant drop to trigger RSI if we had more data
            "ETH/USDT": {"timestamp": 3, "close": 2050}
        }
    ]

    bt = Backtester(orchestrator, data_feed, context)
    results = await bt.run(save_path="backtest_results.json")

    # Adapt results for report (report expects list of values)
    legacy_results = {"pnl": [p["value"] for p in results["pnl"]]}
    report = generate_report(legacy_results, context.memory)
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
