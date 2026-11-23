"""Independent, fail-closed pre-trade risk checks for spot paper trading."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Mapping


@dataclass(frozen=True)
class RiskLimits:
    """Hard portfolio and per-order risk limits."""

    risk_per_trade: float = 0.01
    max_order_notional: float = 1_000.0
    max_position_fraction: float = 0.20
    max_portfolio_exposure_fraction: float = 0.80
    max_daily_loss_fraction: float = 0.05
    min_stop_distance_fraction: float = 0.001
    estimated_fee_rate: float = 0.001


@dataclass(frozen=True)
class RiskDecision:
    """Immutable result of a pre-trade risk assessment."""

    approved: bool
    symbol: str
    side: str
    quantity: float = 0.0
    notional: float = 0.0
    risk_amount: float = 0.0
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "notional": self.notional,
            "risk_amount": self.risk_amount,
            "reasons": list(self.reasons),
        }


class RiskEngine:
    """Calculate bounded order sizes; this component never submits orders."""

    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()
        self._validate_limits()

    def _validate_limits(self) -> None:
        values = vars(self.limits)
        if any(not isfinite(float(value)) for value in values.values()):
            raise ValueError("Todos os limites têm de ser finitos.")
        if not 0 < self.limits.risk_per_trade <= 1:
            raise ValueError("risk_per_trade tem de estar em (0, 1].")
        if self.limits.max_order_notional <= 0:
            raise ValueError("max_order_notional tem de ser positivo.")
        for name in (
            "max_position_fraction",
            "max_portfolio_exposure_fraction",
            "max_daily_loss_fraction",
        ):
            if not 0 < getattr(self.limits, name) <= 1:
                raise ValueError(f"{name} tem de estar em (0, 1].")
        if not 0 < self.limits.min_stop_distance_fraction < 1:
            raise ValueError("min_stop_distance_fraction tem de estar em (0, 1).")
        if not 0 <= self.limits.estimated_fee_rate < 1:
            raise ValueError("estimated_fee_rate tem de estar em [0, 1).")

    @staticmethod
    def _number(data: Mapping[str, Any], key: str) -> float:
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} tem de ser numérico.")
        result = float(value)
        if not isfinite(result):
            raise ValueError(f"{key} tem de ser finito.")
        return result

    def assess(
        self,
        intent: Mapping[str, Any],
        portfolio: Any,
        *,
        daily_pnl: float = 0.0,
    ) -> RiskDecision:
        """Assess an intent; strategy-supplied risk flags are deliberately ignored."""
        symbol = ""
        side = ""
        try:
            if not isinstance(intent, Mapping):
                raise ValueError("A intenção de negociação tem de ser um mapeamento.")
            symbol = str(intent.get("symbol", "")).strip()
            side = str(intent.get("side", "")).upper()
            if not symbol:
                raise ValueError("symbol é obrigatório.")
            if side not in {"BUY", "SELL"}:
                raise ValueError("side tem de ser BUY ou SELL.")

            entry = self._number(intent, "entry_price")
            stop = self._number(intent, "stop_price")
            equity = float(portfolio.total_value)
            cash = float(portfolio.cash)
            exposure = float(portfolio.exposure)
            daily = float(daily_pnl)
            if not all(isfinite(value) for value in (equity, cash, exposure, daily)):
                raise ValueError("O estado do portefólio contém valores não finitos.")
            if equity <= 0 or cash < 0 or exposure < 0:
                raise ValueError("O estado do portefólio é inválido.")
            if entry <= 0 or stop <= 0:
                raise ValueError("entry_price e stop_price têm de ser positivos.")

            distance = abs(entry - stop)
            if distance / entry < self.limits.min_stop_distance_fraction:
                raise ValueError("A distância ao stop é demasiado pequena.")
            # The current portfolio model is spot-long only. Both BUY and SELL
            # intents therefore carry a protective stop below the entry price.
            if stop >= entry:
                raise ValueError("O stop de uma posição spot longa tem de ficar abaixo da entrada.")
            if daily <= -equity * self.limits.max_daily_loss_fraction:
                raise ValueError("Limite de perda diária atingido.")

            if side == "SELL":
                position = portfolio.positions.get(symbol)
                available = float(position.quantity) if position else 0.0
                requested = (
                    self._number(intent, "quantity")
                    if "quantity" in intent
                    else available
                )
                if requested <= 0 or requested > available:
                    raise ValueError("Quantidade de venda superior ao inventário disponível.")
                notional = requested * entry
                if not isfinite(notional):
                    raise ValueError("Notional da ordem não finito.")
                return RiskDecision(
                    True, symbol, side, requested, notional, requested * distance
                )

            risk_budget = equity * self.limits.risk_per_trade
            quantity_by_risk = risk_budget / distance
            position = portfolio.positions.get(symbol)
            existing_notional = (
                float(position.quantity)
                * float(portfolio.marks.get(symbol, position.average_entry_price))
                if position
                else 0.0
            )
            position_capacity = max(
                0.0, equity * self.limits.max_position_fraction - existing_notional
            )
            portfolio_capacity = max(
                0.0,
                equity * self.limits.max_portfolio_exposure_fraction - exposure,
            )
            notional_cap = min(
                self.limits.max_order_notional,
                position_capacity,
                portfolio_capacity,
                cash / (1 + self.limits.estimated_fee_rate),
            )
            quantity = min(quantity_by_risk, notional_cap / entry)
            notional = quantity * entry
            risk_amount = quantity * distance
            if not all(isfinite(value) for value in (quantity, notional, risk_amount)):
                raise ValueError("O cálculo de dimensionamento produziu valores não finitos.")
            if quantity <= 0 or notional <= 0:
                raise ValueError("Os limites de exposição ou o saldo não permitem abrir posição.")
            return RiskDecision(
                True, symbol, side, quantity, notional, risk_amount
            )
        except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
            return RiskDecision(False, symbol, side, reasons=(str(error),))
