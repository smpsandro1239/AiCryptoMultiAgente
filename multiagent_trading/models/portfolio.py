"""Portfolio accounting primitives for deterministic paper-trading simulations."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite


@dataclass
class Position:
    """A net spot position with volume-weighted average entry price."""

    quantity: float = 0.0
    average_entry_price: float = 0.0


@dataclass
class PortfolioState:
    """Cash, spot positions and mark-to-market valuation; simulated fills only."""

    initial_value: float = 10_000.0
    cash: float = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict)
    marks: dict[str, float] = field(default_factory=dict)
    fees_paid: float = 0.0
    _realized_pnl: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        self._validate_non_negative(self.initial_value, "initial_value")
        self.cash = float(self.initial_value)

    @staticmethod
    def _validate_non_negative(value: float, name: str) -> None:
        if isinstance(value, bool) or not isfinite(float(value)) or float(value) < 0:
            raise ValueError(f"{name} tem de ser finito e não negativo.")

    @property
    def total_value(self) -> float:
        """Cash plus the marked value of all open spot positions."""
        return self.cash + self.exposure

    @total_value.setter
    def total_value(self, value: float) -> None:
        """Compatibility setter for legacy simulations without open positions."""
        self._validate_non_negative(value, "total_value")
        if self.positions:
            raise ValueError("Não é possível definir total_value com posições abertas.")
        self.cash = float(value)

    @property
    def unrealized_pnl(self) -> float:
        return sum(
            position.quantity
            * (self.marks.get(symbol, position.average_entry_price) - position.average_entry_price)
            for symbol, position in self.positions.items()
        )

    @property
    def realized_pnl(self) -> float:
        return self._realized_pnl

    @property
    def exposure(self) -> float:
        return sum(
            position.quantity * self.marks.get(symbol, position.average_entry_price)
            for symbol, position in self.positions.items()
        )

    def mark_price(self, symbol: str, price: float) -> None:
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("symbol é obrigatório.")
        self._validate_non_negative(price, "price")
        if price == 0:
            raise ValueError("O preço tem de ser superior a zero.")
        self.marks[symbol] = float(price)

    def apply_fill(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        fee_rate: float = 0.0,
    ) -> None:
        """Apply a simulated spot fill atomically after validating all constraints."""
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("symbol é obrigatório.")
        if side not in {"BUY", "SELL"}:
            raise ValueError("side tem de ser BUY ou SELL.")
        for value, name in (
            (quantity, "quantity"),
            (price, "price"),
            (fee_rate, "fee_rate"),
        ):
            self._validate_non_negative(value, name)
        if quantity == 0 or price == 0 or fee_rate >= 1:
            raise ValueError("quantity e price têm de ser positivos e fee_rate inferior a 1.")

        notional = float(quantity) * float(price)
        fee = notional * float(fee_rate)
        position = self.positions.get(symbol)

        if side == "BUY":
            if notional + fee > self.cash:
                raise ValueError("Saldo insuficiente para o fill simulado.")
            current = position or Position()
            new_quantity = current.quantity + float(quantity)
            new_average = (
                current.quantity * current.average_entry_price + notional + fee
            ) / new_quantity
            self.positions[symbol] = Position(new_quantity, new_average)
            self.cash -= notional + fee
        else:
            if position is None or quantity > position.quantity:
                raise ValueError("Não é permitido vender mais do que a posição disponível.")
            realized = float(quantity) * (float(price) - position.average_entry_price) - fee
            self._realized_pnl += realized
            remaining = position.quantity - float(quantity)
            if remaining == 0:
                self.positions.pop(symbol)
            else:
                self.positions[symbol] = Position(remaining, position.average_entry_price)
            self.cash += notional - fee

        self.fees_paid += fee
        self.marks[symbol] = float(price)

    def snapshot(self) -> dict[str, object]:
        return {
            "cash": self.cash,
            "equity": self.total_value,
            "exposure": self.exposure,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "fees_paid": self.fees_paid,
            "positions": {
                symbol: {
                    "quantity": position.quantity,
                    "average_entry_price": position.average_entry_price,
                    "mark_price": self.marks.get(symbol, position.average_entry_price),
                }
                for symbol, position in self.positions.items()
            },
        }
