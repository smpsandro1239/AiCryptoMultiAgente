import asyncio
import pandas as pd
from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Context, Backtester
from multiagent_trading.core.logger import Logger
from multiagent_trading.agents import ScannerAgent, ExecutionAgent, RiskAgent, SupervisorAgent, LLMAgent
from multiagent_trading.models.portfolio import PortfolioState

async def test_backtester_metrics():
    eb = EventBus()
    logger = Logger()
    ctx = Context(portfolio=PortfolioState())
    agents = [
        ScannerAgent("scanner", {}, ctx, eb, logger),
        RiskAgent("risk", {}, ctx, eb, logger),
        LLMAgent("llm", {}, ctx, eb, logger),
        SupervisorAgent("supervisor", {}, ctx, eb, logger),
        ExecutionAgent("execution", {}, ctx, eb, logger)
    ]
    orchestrator = Orchestrator(agents, ctx, eb, logger)

    data_feed = [{"symbol": "BTC/USDT", "close": 100 + i, "timestamp": i} for i in range(10)]
    bt = Backtester(orchestrator, data_feed, ctx)
    results = await bt.run()

    print("Metrics:", results.get("metrics"))
    assert "sharpe_ratio" in results["metrics"]
    assert "max_drawdown" in results["metrics"]
    assert results["metrics"]["final_value"] > 10000

if __name__ == "__main__":
    asyncio.run(test_backtester_metrics())
