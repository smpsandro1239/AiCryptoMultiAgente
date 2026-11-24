import pytest

from multiagent_trading.core.portfolio_store import PortfolioStore
from multiagent_trading.models.portfolio import PortfolioState


def test_portfolio_snapshot_round_trip_preserves_accounting(tmp_path):
    database = tmp_path / "portfolio.sqlite3"
    original = PortfolioState(initial_value=2_000)
    original.apply_fill("BTC/USDT", "BUY", 2, 100, fee_rate=0.001)
    original.mark_price("BTC/USDT", 125)
    original.apply_fill("BTC/USDT", "SELL", 0.5, 125, fee_rate=0.001)

    store = PortfolioStore(str(database))
    assert store.save(original) == 1
    store.close()

    restarted = PortfolioStore(str(database))
    restored = restarted.load_latest()
    assert restored is not None
    assert restored.initial_value == pytest.approx(original.initial_value)
    assert restored.cash == pytest.approx(original.cash)
    assert restored.total_value == pytest.approx(original.total_value)
    assert restored.peak_equity == pytest.approx(original.peak_equity)
    assert restored.realized_pnl == pytest.approx(original.realized_pnl)
    assert restored.fees_paid == pytest.approx(original.fees_paid)
    assert restored.positions["BTC/USDT"].quantity == pytest.approx(
        original.positions["BTC/USDT"].quantity
    )
    assert restored.marks == original.marks
    restarted.close()


def test_portfolio_store_returns_none_when_empty():
    store = PortfolioStore()
    assert store.load_latest() is None
    store.close()


def test_portfolio_restore_rejects_inconsistent_high_water_mark():
    snapshot = PortfolioState(initial_value=1_000).snapshot()
    snapshot["cash"] = 2_000
    with pytest.raises(ValueError, match="inconsistente"):
        PortfolioState.from_snapshot(snapshot)


def test_portfolio_store_keeps_append_only_history(tmp_path):
    store = PortfolioStore(str(tmp_path / "portfolio.sqlite3"))
    portfolio = PortfolioState(initial_value=1_000)
    first = store.save(portfolio)
    portfolio.apply_fill("BTC/USDT", "BUY", 1, 100)
    second = store.save(portfolio)
    assert second > first
    assert [item["id"] for item in store.list_snapshots()] == [second, first]
    store.close()


def test_portfolio_store_rejects_invalid_history_limit():
    store = PortfolioStore()
    with pytest.raises(ValueError):
        store.list_snapshots(0)
    store.close()
