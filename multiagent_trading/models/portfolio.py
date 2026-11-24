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
    peak_equity: float = field(init=False)
    _realized_pnl: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        self._validate_non_negative(self.initial_value, "initial_value")
        self.cash = float(self.initial_value)
        self.peak_equity = float(self.initial_value)

    def _update_peak_equity(self) -> None:
        equity = self.total_value
        if not isfinite(equity):
            raise ValueError("Equity do portefólio não finita.")
        self.peak_equity = max(self.peak_equity, equity)

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
        self._update_peak_equity()

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
        candidate_exposure = sum(
            position.quantity
            * (
                float(price)
                if current_symbol == symbol
                else self.marks.get(current_symbol, position.average_entry_price)
            )
            for current_symbol, position in self.positions.items()
        )
        candidate_equity = self.cash + candidate_exposure
        if not isfinite(candidate_exposure) or not isfinite(candidate_equity):
            raise ValueError("A marcação produziria exposição ou equity não finita.")
        self.marks[symbol] = float(price)
        self.peak_equity = max(self.peak_equity, candidate_equity)

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
        new_fees_paid = self.fees_paid + fee
        if not all(isfinite(value) for value in (notional, fee, new_fees_paid)):
            raise ValueError("Notional e comissão têm de ser finitos.")
        position = self.positions.get(symbol)

        if side == "BUY":
            total_cost = notional + fee
            new_cash = self.cash - total_cost
            if total_cost > self.cash:
                raise ValueError("Saldo insuficiente para o fill simulado.")
            current = position or Position()
            new_quantity = current.quantity + float(quantity)
            new_average = (
                current.quantity * current.average_entry_price + total_cost
            ) / new_quantity
            if not all(isfinite(value) for value in (new_cash, new_quantity, new_average)):
                raise ValueError("O fill produziria valores contabilísticos não finitos.")
            self.positions[symbol] = Position(new_quantity, new_average)
            self.cash = new_cash
        else:
            if position is None or quantity > position.quantity:
                raise ValueError("Não é permitido vender mais do que a posição disponível.")
            realized = float(quantity) * (float(price) - position.average_entry_price) - fee
            new_realized_pnl = self._realized_pnl + realized
            new_cash = self.cash + notional - fee
            remaining = position.quantity - float(quantity)
            if not all(isfinite(value) for value in (realized, new_realized_pnl, new_cash)):
                raise ValueError("O fill produziria valores contabilísticos não finitos.")
            self._realized_pnl = new_realized_pnl
            if remaining == 0:
                self.positions.pop(symbol)
            else:
                self.positions[symbol] = Position(remaining, position.average_entry_price)
            self.cash = new_cash

        self.fees_paid = new_fees_paid
        self.marks[symbol] = float(price)
        self._update_peak_equity()

    def snapshot(self) -> dict[str, object]:
        return {
            "initial_value": self.initial_value,
            "cash": self.cash,
            "equity": self.total_value,
            "peak_equity": self.peak_equity,
            "drawdown_fraction": (
                max(0.0, (self.peak_equity - self.total_value) / self.peak_equity)
                if self.peak_equity > 0
                else 0.0
            ),
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

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, object]) -> PortfolioState:
        """Restore a portfolio from a validated snapshot without replaying fills."""
        if not isinstance(snapshot, dict):
            raise ValueError("Snapshot do portefólio inválido.")
        required = {
            "initial_value", "cash", "peak_equity", "realized_pnl", "fees_paid", "positions"
        }
        if not required.issubset(snapshot):
            raise ValueError("Snapshot do portefólio incompleto.")
        try:
            initial_value = float(snapshot["initial_value"])
            cash = float(snapshot["cash"])
            peak_equity = float(snapshot["peak_equity"])
            realized_pnl = float(snapshot["realized_pnl"])
            fees_paid = float(snapshot["fees_paid"])
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("Snapshot contém campos numéricos inválidos.") from error
        if not all(
            isfinite(value)
            for value in (initial_value, cash, peak_equity, realized_pnl, fees_paid)
        ):
            raise ValueError("Snapshot contém valores não finitos.")
        if min(initial_value, cash, peak_equity, fees_paid) < 0:
            raise ValueError(
                "Cash, capital inicial, high-water mark e comissões não podem ser negativos."
            )
        raw_positions = snapshot["positions"]
        if not isinstance(raw_positions, dict):
            raise ValueError("positions tem de ser um objeto.")
        positions: dict[str, Position] = {}
        marks: dict[str, float] = {}
        for symbol, raw in raw_positions.items():
            if not isinstance(symbol, str) or not symbol or not isinstance(raw, dict):
                raise ValueError("Posição inválida no snapshot.")
            try:
                quantity = float(raw["quantity"])
                average = float(raw["average_entry_price"])
                mark = float(raw["mark_price"])
            except (KeyError, TypeError, ValueError, OverflowError) as error:
                raise ValueError("Campos da posição inválidos.") from error
            if any(not isfinite(value) or value <= 0 for value in (quantity, average, mark)):
                raise ValueError("Quantidade e preços da posição têm de ser positivos e finitos.")
            positions[symbol] = Position(quantity, average)
            marks[symbol] = mark
        portfolio = cls(initial_value=initial_value)
        portfolio.cash = cash
        portfolio.peak_equity = peak_equity
        portfolio._realized_pnl = realized_pnl
        portfolio.fees_paid = fees_paid
        portfolio.positions = positions
        portfolio.marks = marks
        if not isfinite(portfolio.total_value) or portfolio.peak_equity < portfolio.total_value:
            raise ValueError("Snapshot inconsistente: equity inválida face ao high-water mark.")
        return portfolio
