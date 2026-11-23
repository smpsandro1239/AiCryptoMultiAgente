import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from multiagent_trading.core.logger import Logger
from multiagent_trading.core.memory import PersistentSemanticMemory

EventCallback = Callable[[Any], Awaitable[None] | None]


class EventBus:
    """Simple asynchronous event dispatcher.

    Subscribers are called concurrently. Synchronous callbacks are also
    supported; callback exceptions are propagated to the publisher.
    """

    def __init__(self) -> None:
        self.listeners: dict[str, list[EventCallback]] = {}

    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Register a callback for an event."""
        self.listeners.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type: str, callback: EventCallback) -> bool:
        """Remove one callback; return False when it was not registered."""
        callbacks = self.listeners.get(event_type)
        if not callbacks or callback not in callbacks:
            return False

        callbacks.remove(callback)
        if not callbacks:
            del self.listeners[event_type]
        return True

    async def publish(self, event_type: str, data: Any) -> None:
        """Dispatch an event to a snapshot of its current subscribers."""
        callbacks = tuple(self.listeners.get(event_type, ()))
        if not callbacks:
            return

        results = [callback(data) for callback in callbacks]
        awaitables = [result for result in results if inspect.isawaitable(result)]
        if awaitables:
            await asyncio.gather(*awaitables)


class Context:
    """Shared state passed to agents during one simulation."""

    def __init__(
        self,
        timestamp: Any = None,
        regime: str | None = None,
        portfolio: Any = None,
        market_data: Any = None,
        memory: Any = None,
        risk_engine: Any = None,
    ) -> None:
        self.timestamp = timestamp
        self.regime = regime
        self.portfolio = portfolio
        self.market_data = market_data
        self.memory = memory if memory is not None else PersistentSemanticMemory()
        self.risk_engine = risk_engine


class Orchestrator:
    """Coordinates market updates through the event bus."""

    def __init__(
        self,
        agents: dict[str, Any],
        context: Context,
        event_bus: EventBus,
        logger: Logger,
    ):
        self.agents = agents
        self.context = context
        self.event_bus = event_bus
        self.logger = logger

    async def step(self, market_snapshot: dict[str, Any]) -> None:
        """Update shared market state and notify subscribed agents."""
        self.context.market_data = market_snapshot
        self.context.timestamp = market_snapshot.get("timestamp")
        await self.event_bus.publish("market_update", market_snapshot)


class Backtester:
    """Runs an orchestrator over an iterable of market snapshots.

    This class records portfolio values supplied by the agents. It does not
    model fills, fees, slippage, funding, or exchange execution by itself.
    """

    def __init__(self, orchestrator: Orchestrator, data_feed: Any, context: Context):
        self.orchestrator = orchestrator
        self.data_feed = data_feed
        self.context = context
        self.results: dict[str, list[Any]] = {"pnl": []}

    async def run(self) -> dict[str, list[Any]]:
        """Process each tick and record the portfolio value after each step."""
        for tick in self.data_feed:
            await self.orchestrator.step(tick)
            self.results["pnl"].append(self.context.portfolio.total_value)
        return self.results
