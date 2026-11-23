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


from multiagent_trading.data.loader import load_ohlcv_csv


def test_csv_loader_rejects_missing_file_by_default(tmp_path):
    missing_path = tmp_path / "missing.csv"
    try:
        load_ohlcv_csv(missing_path)
    except FileNotFoundError as error:
        assert "missing.csv" in str(error)
    else:
        raise AssertionError("Missing data must not be replaced silently")


def test_csv_loader_allows_synthetic_data_only_when_requested(tmp_path):
    candles = load_ohlcv_csv(tmp_path / "missing.csv", allow_synthetic=True)
    assert len(candles) == 3
    assert set(candles[0]) == {"timestamp", "open", "high", "low", "close", "volume"}


def test_csv_loader_validates_ohlcv_relationships(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text(
        "timestamp,open,high,low,close,volume\n1,100,99,98,100,10\n",
        encoding="utf-8",
    )
    try:
        load_ohlcv_csv(csv_path)
    except ValueError as error:
        assert "high" in str(error).lower()
    else:
        raise AssertionError("Invalid OHLC relationships must be rejected")
