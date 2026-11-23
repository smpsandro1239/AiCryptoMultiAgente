"""Portfolio accounting primitives for deterministic paper-trading simulations."""
from __future__ import annotations
from dataclasses import dataclass, field
from math import isfinite

@dataclass
class Position:
    """A net spot position with volume-weighted average entry price."""
    quantity: float = 0.0
    average_entry_price: float = 0.0
    realized_pnl: float = 0.0

@dataclass
class PortfolioState:
    """Cash, open positions and mark-to-market valuation; simulated fills only."""
    initial_value: float = 10_000.0
    cash: float = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict)
    marks: dict[str, float] = field(default_factory=dict)
    fees_paid: float = 0.0
    def __post_init__(self) -> None:
        self._validate_non_negative(self.initial_value, "initial_value")
        self.cash = float(self.initial_value)
    @staticmethod
    def _validate_non_negative(value: float, name: str) -> None:
        if not isfinite(float(value)) or float(value) < 0:
            raise ValueError(f"{name} tem de ser finito e não negativo.")
    @property
    def total_value(self) -> float:
        return self.cash + sum(p.quantity * self.marks.get(s, p.average_entry_price) for s, p in self.positions.items())
    @total_value.setter
    def total_value(self, value: float) -> None:
        self._validate_non_negative(value, "total_value")
        if self.positions:
            raise ValueError("Não é possível definir total_value com posições abertas.")
        self.cash = float(value)
    @property
    def unrealized_pnl(self) -> float:
        return sum(p.quantity * (self.marks.get(s, p.average_entry_price) - p.average_entry_price) for s, p in self.positions.items())
    @property
    def realized_pnl(self) -> float:
        return sum(p.realized_pnl for p in self.positions.values())
    @property
    def exposure(self) -> float:
        return sum(p.quantity * self.marks.get(s, p.average_entry_price) for s, p in self.positions.items())
    def mark_price(self, symbol: str, price: float) -> None:
        self._validate_non_negative(price, "price")
        if price == 0:
            raise ValueError("O preço tem de ser superior a zero.")
        self.marks[symbol] = float(price)
    def apply_fill(self, symbol: str, side: str, quantity: float, price: float, fee_rate: float = 0.0) -> None:
        """Apply a simulated spot fill, updating cash, inventory, PnL and fees."""
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("symbol é obrigatório.")
        if side not in {"BUY", "SELL"}:
            raise ValueError("side tem de ser BUY ou SELL.")
        for value, name in ((quantity, "quantity"), (price, "price"), (fee_rate, "fee_rate")):
            self._validate_non_negative(value, name)
        if quantity == 0 or price == 0 or fee_rate >= 1:
            raise ValueError("quantity e price têm de ser positivos e fee_rate inferior a 1.")
        notional, fee = quantity * price, quantity * price * fee_rate
        position = self.positions.setdefault(symbol, Position())
        if side == "BUY":
            if notional + fee > self.cash:
                raise ValueError("Saldo insuficiente para o fill simulado.")
            new_quantity = position.quantity + quantity
            position.average_entry_price = (position.quantity * position.average_entry_price + notional) / new_quantity
            position.quantity = new_quantity
            self.cash -= notional + fee
        else:
            if quantity > position.quantity:
                raise ValueError("Não é permitido vender mais do que a posição disponível.")
            position.realized_pnl += quantity * (price - position.average_entry_price) - fee
            position.quantity -= quantity
            self.cash += notional - fee
            if position.quantity == 0:
                position.average_entry_price = 0.0
        self.fees_paid += fee
        self.marks[symbol] = float(price)
        if position.quantity == 0:
            self.positions.pop(symbol, None)
    def snapshot(self) -> dict[str, object]:
        return {"cash": self.cash, "equity": self.total_value, "exposure": self.exposure,
            "realized_pnl": self.realized_pnl, "unrealized_pnl": self.unrealized_pnl,
            "fees_paid": self.fees_paid,
            "positions": {s: {"quantity": p.quantity, "average_entry_price": p.average_entry_price,
                "realized_pnl": p.realized_pnl, "mark_price": self.marks.get(s, p.average_entry_price)}
                for s, p in self.positions.items()}}
