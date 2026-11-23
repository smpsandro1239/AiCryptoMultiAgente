"""Independent, fail-closed pre-trade risk checks for paper trading."""
from __future__ import annotations
from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Mapping

@dataclass(frozen=True)
class RiskLimits:
    risk_per_trade: float = 0.01
    max_order_notional: float = 1_000.0
    max_position_fraction: float = 0.20
    max_portfolio_exposure_fraction: float = 0.80
    max_daily_loss_fraction: float = 0.05
    min_stop_distance_fraction: float = 0.001

@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    symbol: str
    side: str
    quantity: float = 0.0
    notional: float = 0.0
    risk_amount: float = 0.0
    reasons: tuple[str, ...] = field(default_factory=tuple)
    def as_dict(self) -> dict[str, Any]:
        return {"approved": self.approved, "symbol": self.symbol, "side": self.side,
            "quantity": self.quantity, "notional": self.notional,
            "risk_amount": self.risk_amount, "reasons": list(self.reasons)}

class RiskEngine:
    """Calculate bounded order sizes. This component never submits orders."""
    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()
        self._validate_limits()
    def _validate_limits(self) -> None:
        if any(not isfinite(float(v)) for v in vars(self.limits).values()):
            raise ValueError("Todos os limites têm de ser finitos.")
        if not 0 < self.limits.risk_per_trade <= 1:
            raise ValueError("risk_per_trade tem de estar em (0, 1].")
        if self.limits.max_order_notional <= 0:
            raise ValueError("max_order_notional tem de ser positivo.")
        for name in ("max_position_fraction", "max_portfolio_exposure_fraction", "max_daily_loss_fraction"):
            if not 0 < getattr(self.limits, name) <= 1:
                raise ValueError(f"{name} tem de estar em (0, 1].")
        if not 0 < self.limits.min_stop_distance_fraction < 1:
            raise ValueError("min_stop_distance_fraction tem de estar em (0, 1).")
    @staticmethod
    def _number(data: Mapping[str, Any], key: str) -> float:
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} tem de ser numérico.")
        result = float(value)
        if not isfinite(result):
            raise ValueError(f"{key} tem de ser finito.")
        return result
    def assess(self, intent: Mapping[str, Any], portfolio: Any, *, daily_pnl: float = 0.0) -> RiskDecision:
        """Assess intent fields; strategy-supplied risk flags are deliberately ignored."""
        symbol, side = str(intent.get("symbol", "")), str(intent.get("side", "")).upper()
        try:
            if not symbol:
                raise ValueError("symbol é obrigatório.")
            if side not in {"BUY", "SELL"}:
                raise ValueError("side tem de ser BUY ou SELL.")
            entry, stop = self._number(intent, "entry_price"), self._number(intent, "stop_price")
            equity, cash = float(portfolio.total_value), float(portfolio.cash)
            exposure, daily = float(portfolio.exposure), float(daily_pnl)
            if not all(isfinite(v) for v in (equity, cash, exposure, daily)):
                raise ValueError("O estado do portefólio contém valores não finitos.")
            if equity <= 0 or cash < 0 or exposure < 0:
                raise ValueError("O estado do portefólio é inválido.")
            if entry <= 0 or stop <= 0:
                raise ValueError("entry_price e stop_price têm de ser positivos.")
            distance = abs(entry - stop)
            if distance / entry < self.limits.min_stop_distance_fraction:
                raise ValueError("A distância ao stop é demasiado pequena.")
            if (side == "BUY" and stop >= entry) or (side == "SELL" and stop <= entry):
                raise ValueError("O stop-loss está do lado incorreto da entrada.")
            if daily <= -equity * self.limits.max_daily_loss_fraction:
                raise ValueError("Limite de perda diária atingido.")
            if side == "SELL":
                position = portfolio.positions.get(symbol)
                available = float(position.quantity) if position else 0.0
                requested = self._number(intent, "quantity") if "quantity" in intent else available
                quantity = min(requested, available)
                if quantity <= 0:
                    raise ValueError("Não existe posição disponível para vender.")
                return RiskDecision(True, symbol, side, quantity, quantity * entry, quantity * distance)
            budget = equity * self.limits.risk_per_trade
            quantity_by_risk = budget / distance
            position = portfolio.positions.get(symbol)
            existing = float(position.quantity) * float(portfolio.marks.get(symbol, position.average_entry_price)) if position else 0.0
            position_cap = max(0.0, equity * self.limits.max_position_fraction - existing)
            portfolio_cap = max(0.0, equity * self.limits.max_portfolio_exposure_fraction - exposure)
            notional_cap = min(self.limits.max_order_notional, position_cap, portfolio_cap, cash)
            quantity = min(quantity_by_risk, notional_cap / entry)
            notional = quantity * entry
            if quantity <= 0 or notional <= 0:
                raise ValueError("Os limites de exposição ou o saldo não permitem abrir posição.")
            return RiskDecision(True, symbol, side, quantity, notional, quantity * distance)
        except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
            return RiskDecision(False, symbol, side, reasons=(str(error),))
