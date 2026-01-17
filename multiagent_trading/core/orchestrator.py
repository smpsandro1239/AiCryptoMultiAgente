import asyncio
import logging
from typing import Dict, Any, List
from multiagent_trading.core.memory import VectorMemory

class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type: str, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    async def publish(self, event_type: str, data: Any):
        if event_type in self.listeners:
            tasks = [callback(data) for callback in self.listeners[event_type]]
            await asyncio.gather(*tasks)

class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("MATF")

    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
    def warning(self, msg): self.logger.warning(msg)

class SemanticMemory:
    def __init__(self):
        self.memory = []

    def add(self, key: str, value: Any):
        self.memory.append({"key": key, "value": value})

    def query(self, query_str: str):
        return [m for m in self.memory if query_str.lower() in str(m["value"]).lower()]

class Context:
    def __init__(self, timestamp=None, regime=None, portfolio=None, market_data=None, memory=None, config=None):
        self.timestamp = timestamp
        self.regime = regime
        self.portfolio = portfolio
        self.market_data = market_data or {}
        self.memory = memory or SemanticMemory()
        self.vector_memory = VectorMemory()
        self.config = config or {}

class Orchestrator:
    def __init__(self, agents, context, event_bus, logger):
        self.agents = agents
        self.context = context
        self.event_bus = event_bus
        self.logger = logger

    async def step(self, market_snapshot_batch: Dict[str, Any]):
        self.context.market_data.update(market_snapshot_batch)
        if market_snapshot_batch:
            first_symbol = next(iter(market_snapshot_batch))
            self.context.timestamp = market_snapshot_batch[first_symbol].get("timestamp")
        await self.event_bus.publish("market_update", market_snapshot_batch)

class Backtester:
    def __init__(self, orchestrator, data_feed, context, commission=0.001, slippage=0.0005):
        self.orchestrator = orchestrator
        self.data_feed = data_feed
        self.context = context
        self.commission = commission
        self.slippage = slippage
        self.results = {"pnl": []}

    async def run(self, save_path=None):
        import json
        from multiagent_trading.analytics.metrics import get_performance_metrics

        # Inject commission and slippage into config for agents to use if needed
        self.context.config["backtest"] = {
            "commission": self.commission,
            "slippage": self.slippage
        }

        for tick_batch in self.data_feed:
            await self.orchestrator.step(tick_batch)
            market_prices = {s: d.get("close", 0) for s, d in self.context.market_data.items()}
            self.context.portfolio.get_total_value(market_prices)
            self.results["pnl"].append({
                "timestamp": self.context.timestamp,
                "value": self.context.portfolio.total_value
            })

        if save_path:
            metrics = get_performance_metrics(self.results["pnl"])
            with open(save_path, "w") as f:
                json.dump({
                    "pnl": self.results["pnl"],
                    "memory": self.context.memory.memory,
                    "metrics": metrics
                }, f, indent=4)

        return self.results
