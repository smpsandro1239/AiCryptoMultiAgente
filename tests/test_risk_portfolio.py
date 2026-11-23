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
    assert portfolio.unrealized_pnl == pytest.approx(20)
    portfolio.apply_fill("BTC/USDT", "SELL", 1, 110, fee_rate=0.01)
    assert portfolio.cash == pytest.approx(906.9)
    assert portfolio.realized_pnl == pytest.approx(8.9)
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
