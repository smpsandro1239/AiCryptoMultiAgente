import asyncio

from multiagent_trading.core.orchestrator import Backtester, Context, EventBus, Orchestrator
from multiagent_trading.models.portfolio import PortfolioState


def test_event_bus_dispatches_async_and_sync_callbacks():
    async def scenario():
        bus = EventBus()
        received = []

        def sync_callback(payload):
            received.append(("sync", payload))

        async def async_callback(payload):
            received.append(("async", payload))

        bus.subscribe("tick", sync_callback)
        bus.subscribe("tick", async_callback)
        await bus.publish("tick", {"price": 123})

        assert sorted(received) == [
            ("async", {"price": 123}),
            ("sync", {"price": 123}),
        ]

    asyncio.run(scenario())


def test_event_bus_unsubscribe_and_empty_publish():
    async def scenario():
        bus = EventBus()
        received = []

        async def callback(payload):
            received.append(payload)

        assert bus.unsubscribe("missing", callback) is False
        bus.subscribe("tick", callback)
        assert bus.unsubscribe("tick", callback) is True
        assert bus.unsubscribe("tick", callback) is False

        await bus.publish("tick", "ignored")
        assert received == []

    asyncio.run(scenario())


def test_orchestrator_updates_context_and_publishes_market_snapshot():
    async def scenario():
        bus = EventBus()
        context = Context(portfolio=PortfolioState(), memory=object())
        seen = []

        async def on_market_update(snapshot):
            seen.append(snapshot)

        bus.subscribe("market_update", on_market_update)
        orchestrator = Orchestrator({}, context, bus, logger=None)
        snapshot = {"timestamp": "2026-01-01T00:00:00Z", "close": 100.0}

        await orchestrator.step(snapshot)

        assert context.market_data is snapshot
        assert context.timestamp == snapshot["timestamp"]
        assert seen == [snapshot]

    asyncio.run(scenario())


def test_backtester_records_portfolio_value_after_each_tick():
    async def scenario():
        bus = EventBus()
        portfolio = PortfolioState(initial_value=1_000)
        context = Context(portfolio=portfolio, memory=object())

        async def update_portfolio(_snapshot):
            portfolio.total_value += 25

        bus.subscribe("market_update", update_portfolio)
        orchestrator = Orchestrator({}, context, bus, logger=None)
        backtester = Backtester(orchestrator, [{"close": 10}, {"close": 11}], context)

        results = await backtester.run()

        assert results == {"pnl": [1_025, 1_050]}

    asyncio.run(scenario())
