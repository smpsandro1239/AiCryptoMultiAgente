import asyncio
from pathlib import Path

from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.agents.regime import RegimeAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.scanner import ScannerAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.config.loader import load_config
from multiagent_trading.core.logger import Logger
from multiagent_trading.core.memory import PersistentSemanticMemory
from multiagent_trading.core.orchestrator import Backtester, Context, EventBus, Orchestrator
from multiagent_trading.data.loader import load_ohlcv_csv
from multiagent_trading.models.portfolio import PortfolioState


async def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config = load_config(project_root / "config.yaml")
    event_bus = EventBus()
    logger = Logger()
    context = Context(
        portfolio=PortfolioState(),
        memory=PersistentSemanticMemory(project_root / "memory.db"),
    )

    agents = {
        "regime": RegimeAgent("regime", config, context, event_bus, logger),
        "scanner": ScannerAgent("scanner", config, context, event_bus, logger),
        "risk": RiskAgent("risk", config, context, event_bus, logger),
        "supervisor": SupervisorAgent("supervisor", config, context, event_bus, logger),
        "execution": ExecutionAgent("execution", config, context, event_bus, logger),
    }
    orchestrator = Orchestrator(agents, context, event_bus, logger)

    data_path = project_root / "BTCUSDT_1h.csv"
    data_feed = load_ohlcv_csv(data_path, allow_synthetic=True)
    backtester = Backtester(orchestrator, data_feed, context)
    results = await backtester.run()

    print("Portfolio value history (demonstration only):", results["pnl"])
    print("Final portfolio value (not a financial backtest):", context.portfolio.total_value)


if __name__ == "__main__":
    asyncio.run(main())