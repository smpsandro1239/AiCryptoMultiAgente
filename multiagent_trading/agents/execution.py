"""Paper-only execution with mandatory independent risk revalidation."""
from __future__ import annotations

import hashlib
import json

from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.core.order_store import OrderStore
from multiagent_trading.core.risk_engine import RiskEngine


class ExecutionAgent(BaseAgent):
    """Never sends exchange orders; applies a simulated fill after fresh risk checks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.risk_engine is None:
            self.context.risk_engine = RiskEngine()
        self.risk_engine = self.context.risk_engine
        self.order_store = OrderStore(self.config.get("order_db_path", ":memory:"))
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)

    async def on_trade_approved(self, opportunity):
        portfolio = self.context.portfolio
        if portfolio is None:
            await self.event_bus.publish("trade_rejected", {
                **opportunity, "rejection_reason": "Portfolio state unavailable."})
            return

        decision = self.risk_engine.assess(
            opportunity,
            portfolio,
            daily_pnl=float(getattr(self.context, "daily_pnl", 0.0)),
        )
        if not decision.approved:
            await self.event_bus.publish("trade_rejected", {
                **opportunity, "risk_decision": decision.as_dict()})
            return

        order_id = opportunity.get("order_id")
        if not order_id:
            identity = {
                "symbol": decision.symbol,
                "side": decision.side,
                "entry_price": opportunity.get("entry_price"),
                "stop_price": opportunity.get("stop_price"),
                "timestamp": str(self.context.timestamp),
            }
            order_id = hashlib.sha256(
                json.dumps(identity, sort_keys=True).encode("utf-8")
            ).hexdigest()
        order_payload = {
            **opportunity,
            "order_id": order_id,
            "risk_decision": decision.as_dict(),
        }
        if not self.order_store.reserve(order_id, order_payload):
            await self.event_bus.publish("trade_rejected", {
                **opportunity, "order_id": order_id,
                "rejection_reason": "Duplicate or previously claimed order identifier."})
            return

        try:
            portfolio.apply_fill(
                decision.symbol,
                decision.side,
                decision.quantity,
                float(opportunity["entry_price"]),
                fee_rate=self.risk_engine.limits.estimated_fee_rate,
            )
        except (KeyError, TypeError, ValueError) as error:
            self.order_store.set_status(
                order_id, "rejected", {"reason": str(error)}
            )
            await self.event_bus.publish("trade_rejected", {
                **opportunity, "order_id": order_id, "rejection_reason": str(error)})
            return

        result = {
            **opportunity,
            "order_id": order_id,
            "risk_decision": decision.as_dict(),
            "portfolio": portfolio.snapshot(),
            "execution_mode": "paper",
            "order_status": "filled",
        }
        self.order_store.set_status(order_id, "filled", result)
        self.context.memory.add("paper_trade", result)
        await self.event_bus.publish("paper_fill", result)
