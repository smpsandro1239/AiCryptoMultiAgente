import asyncio
from typing import Dict, Any, List
from multiagent_trading.core.logger import Logger
from multiagent_trading.core.memory import PersistentSemanticMemory

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

class Context:
    def __init__(self, timestamp=None, regime=None, portfolio=None, market_data=None, memory=None):
        self.timestamp = timestamp
        self.regime = regime
        self.portfolio = portfolio
        self.market_data = market_data
        self.memory = memory or PersistentSemanticMemory()

class Orchestrator:
    def __init__(self, agents, context, event_bus, logger):
        self.agents = agents
        self.context = context
        self.event_bus = event_bus
        self.logger = logger

    async def step(self, market_snapshot: Dict[str, Any]):
        """
        snapshot pode ser um único tick ou um dicionário {symbol: tick_data}
        """
        self.context.market_data = market_snapshot

        # Se for multi-símbolo, extrair timestamp de um deles
        if isinstance(market_snapshot, dict) and "timestamp" not in market_snapshot:
            first_val = next(iter(market_snapshot.values()))
            if isinstance(first_val, dict):
                self.context.timestamp = first_val.get("timestamp")
        else:
            self.context.timestamp = market_snapshot.get("timestamp")

        await self.event_bus.publish("market_update", market_snapshot)

class Backtester:
    def __init__(self, orchestrator, data_feed, context):
        self.orchestrator = orchestrator
        self.data_feed = data_feed
        self.context = context
        self.results = {"pnl": []}

    async def run(self):
        for tick in self.data_feed:
            await self.orchestrator.step(tick)
            self.results["pnl"].append(self.context.portfolio.total_value)
        return self.results
