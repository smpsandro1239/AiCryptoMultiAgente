import math

import pytest

from multiagent_trading.core.risk_engine import RiskEngine, RiskLimits
from multiagent_trading.models.portfolio import PortfolioState


def test_portfolio_buy_mark_and_sell_accounting():
    portfolio = PortfolioState(initial_value=1_000)
    portfolio.apply_fill("BTC/USDT", "BUY", 2, 100, fee_rate=0.01)
    assert portfolio.cash == pytest.approx(798)
    assert portfolio.total_value == pytest.approx(998)
    portfolio.mark_price("BTC/USDT", 110)
    assert portfolio.unrealized_pnl == pytest.approx(18)
    portfolio.apply_fill("BTC/USDT", "SELL", 1, 110, fee_rate=0.01)
    assert portfolio.cash == pytest.approx(906.9)
    assert portfolio.realized_pnl == pytest.approx(7.9)
    assert portfolio.positions["BTC/USDT"].quantity == pytest.approx(1)


@pytest.mark.parametrize(
    ("quantity", "price", "fee_rate"),
    [(0, 10, 0), (1, 0, 0), (math.inf, 10, 0), (1, 10, -0.1), (1, 10, 1)],
)
def test_portfolio_rejects_invalid_fills(quantity, price, fee_rate):
    with pytest.raises(ValueError):
        PortfolioState().apply_fill("BTC/USDT", "BUY", quantity, price, fee_rate)


def test_portfolio_rejects_overselling_and_insufficient_cash_without_mutation():
    portfolio = PortfolioState(initial_value=100)
    with pytest.raises(ValueError):
        portfolio.apply_fill("BTC/USDT", "BUY", 2, 100)
    assert portfolio.positions == {}
    portfolio.apply_fill("BTC/USDT", "BUY", 0.5, 100)
    with pytest.raises(ValueError):
        portfolio.apply_fill("BTC/USDT", "SELL", 1, 110)
    assert portfolio.positions["BTC/USDT"].quantity == pytest.approx(0.5)


def test_realized_pnl_survives_closing_the_entire_position():
    portfolio = PortfolioState(initial_value=1_000)
    portfolio.apply_fill("BTC/USDT", "BUY", 1, 100)
    portfolio.apply_fill("BTC/USDT", "SELL", 1, 110, fee_rate=0.01)
    assert portfolio.positions == {}
    assert portfolio.realized_pnl == pytest.approx(8.9)


def test_risk_engine_sizes_position_from_risk_and_caps_notional():
    portfolio = PortfolioState(initial_value=10_000)
    engine = RiskEngine(RiskLimits(max_order_notional=500))
    decision = engine.assess(
        {
            "symbol": "BTC/USDT",
            "side": "BUY",
            "entry_price": 100,
            "stop_price": 95,
            "risk_ok": False,
        },
        portfolio,
    )
    assert decision.approved
    assert decision.quantity == pytest.approx(5)
    assert decision.notional == pytest.approx(500)


def test_risk_engine_rejects_bad_stop_and_non_finite_values():
    engine, portfolio = RiskEngine(), PortfolioState()
    bad_stop = engine.assess(
        {"symbol": "BTC/USDT", "side": "BUY", "entry_price": 100, "stop_price": 101},
        portfolio,
    )
    bad_price = engine.assess(
        {"symbol": "BTC/USDT", "side": "BUY", "entry_price": math.nan, "stop_price": 90},
        portfolio,
    )
    assert not bad_stop.approved
    assert not bad_price.approved


def test_risk_engine_enforces_daily_loss_and_aggregate_exposure():
    portfolio = PortfolioState(initial_value=1_000)
    engine = RiskEngine(RiskLimits(max_portfolio_exposure_fraction=0.5))
    portfolio.apply_fill("ETH/USDT", "BUY", 5, 100)
    blocked = engine.assess(
        {"symbol": "BTC/USDT", "side": "BUY", "entry_price": 100, "stop_price": 90},
        portfolio,
    )
    daily_loss = engine.assess(
        {"symbol": "BTC/USDT", "side": "BUY", "entry_price": 100, "stop_price": 90},
        PortfolioState(initial_value=1_000),
        daily_pnl=-50,
    )
    assert not blocked.approved
    assert not daily_loss.approved


def test_risk_engine_only_approves_sells_with_existing_inventory():
    portfolio, engine = PortfolioState(initial_value=1_000), RiskEngine()
    intent = {
        "symbol": "BTC/USDT",
        "side": "SELL",
        "entry_price": 100,
        "stop_price": 90,
    }
    assert not engine.assess(intent, portfolio).approved
    portfolio.apply_fill("BTC/USDT", "BUY", 1, 100)
    approved = engine.assess(intent, portfolio)
    assert approved.approved
    assert approved.quantity == pytest.approx(1)


def test_risk_engine_rejects_sell_quantity_above_inventory():
    portfolio = PortfolioState(initial_value=1_000)
    portfolio.apply_fill("BTC/USDT", "BUY", 1, 100)
    decision = RiskEngine().assess(
        {
            "symbol": "BTC/USDT",
            "side": "SELL",
            "quantity": 2,
            "entry_price": 100,
            "stop_price": 90,
        },
        portfolio,
    )
    assert not decision.approved


def test_risk_sizing_reserves_cash_for_the_same_fee_used_by_execution():
    portfolio = PortfolioState(initial_value=100)
    engine = RiskEngine(
        RiskLimits(
            risk_per_trade=1,
            max_order_notional=1_000,
            max_position_fraction=1,
            max_portfolio_exposure_fraction=1,
            estimated_fee_rate=0.01,
        )
    )
    decision = engine.assess(
        {"symbol": "BTC/USDT", "side": "BUY", "entry_price": 100, "stop_price": 90},
        portfolio,
    )
    assert decision.approved
    portfolio.apply_fill(
        decision.symbol,
        decision.side,
        decision.quantity,
        100,
        fee_rate=engine.limits.estimated_fee_rate,
    )
    assert portfolio.cash >= 0
    assert portfolio.cash == pytest.approx(0)


def test_portfolio_rejects_overflowing_sell_without_mutation():
    portfolio = PortfolioState(initial_value=1e308)
    portfolio.apply_fill("BTC/USDT", "BUY", 1e308, 1)
    before = portfolio.snapshot()
    with pytest.raises(ValueError, match="finitos"):
        portfolio.apply_fill("BTC/USDT", "SELL", 1e308, 1e308)
    assert portfolio.snapshot() == before


def test_portfolio_rejects_overflowing_buy_without_mutation():
    portfolio = PortfolioState(initial_value=1e308)
    before = portfolio.snapshot()
    with pytest.raises(ValueError, match="finitos"):
        portfolio.apply_fill("BTC/USDT", "BUY", 1e308, 2)
    assert portfolio.snapshot() == before


def test_drawdown_circuit_breaker_blocks_new_entries_but_allows_exits():
    portfolio = PortfolioState(initial_value=1_000)
    portfolio.apply_fill("BTC/USDT", "BUY", 5, 100)
    portfolio.mark_price("BTC/USDT", 80)
    engine = RiskEngine(RiskLimits(max_drawdown_fraction=0.05))

    blocked_entry = engine.assess(
        {"symbol": "ETH/USDT", "side": "BUY", "entry_price": 80, "stop_price": 72},
        portfolio,
    )
    allowed_exit = engine.assess(
        {"symbol": "BTC/USDT", "side": "SELL", "entry_price": 80, "stop_price": 72},
        portfolio,
        daily_pnl=-100,
    )

    assert portfolio.snapshot()["drawdown_fraction"] == pytest.approx(0.1)
    assert not blocked_entry.approved
    assert "drawdown" in blocked_entry.reasons[0].lower()
    assert allowed_exit.approved
    assert allowed_exit.quantity == pytest.approx(5)


def test_portfolio_high_water_mark_never_moves_down():
    portfolio = PortfolioState(initial_value=1_000)
    portfolio.apply_fill("BTC/USDT", "BUY", 2, 100)
    portfolio.mark_price("BTC/USDT", 120)
    assert portfolio.peak_equity == pytest.approx(1_040)
    portfolio.mark_price("BTC/USDT", 90)
    assert portfolio.peak_equity == pytest.approx(1_040)
    assert portfolio.snapshot()["drawdown_fraction"] == pytest.approx(60 / 1_040)
