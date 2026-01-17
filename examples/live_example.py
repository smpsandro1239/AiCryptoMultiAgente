import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Logger, Context, SemanticMemory
from multiagent_trading.agents.regime import RegimeAgent
from multiagent_trading.agents.scanner import ScannerAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.models.portfolio import PortfolioState
from multiagent_trading.config.loader import load_config
from multiagent_trading.execution.ccxt_adapter import CCXTAdapter

async def live_simulation():
    print("Starting Live Trading Simulation (Paper Trading)...")

    config = load_config()
    event_bus = EventBus()
    logger = Logger()

    # Initialize CCXT Adapter
    exchange = CCXTAdapter("binance", paper_trading=True)

    context = Context(
        timestamp=None,
        regime="BULL",
        portfolio=PortfolioState(initial_value=10000),
        memory=SemanticMemory(),
        config=config
    )

    agents = {
        "regime": RegimeAgent("regime", config, context, event_bus, logger),
        "scanner": ScannerAgent("scanner", config, context, event_bus, logger),
        "risk": RiskAgent("risk", config, context, event_bus, logger),
        "supervisor": SupervisorAgent("supervisor", config, context, event_bus, logger),
        "execution": ExecutionAgent("execution", config, context, event_bus, logger),
    }

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    # Simulation loop
    for i in range(5):
        print(f"\n--- Tick {i+1} ---")
        # In live mode, we would fetch real data
        tick_data = {"symbol": "BTC/USDT", "close": 42000 + (i * 100), "timestamp": i}
        await orchestrator.step(tick_data)
        await asyncio.sleep(1) # Wait between ticks

    print("\nSimulation Finished.")
    print(f"Final Portfolio Value: {context.portfolio.total_value}")

if __name__ == "__main__":
    asyncio.run(live_simulation())
