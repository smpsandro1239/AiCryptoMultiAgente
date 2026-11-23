"""Paper-only execution with mandatory independent risk revalidation."""
from __future__ import annotations

import hashlib
import json

from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.core.risk_engine import RiskEngine


class ExecutionAgent(BaseAgent):
    """Never sends exchange orders; applies a simulated fill after fresh risk checks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.risk_engine is None:
            self.context.risk_engine = RiskEngine()
        self.risk_engine = self.context.risk_engine
        self._processed_order_ids: set[str] = set()
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
        if order_id in self._processed_order_ids:
            await self.event_bus.publish("trade_rejected", {
                **opportunity, "order_id": order_id,
                "rejection_reason": "Duplicate order identifier."})
            return

        try:
            portfolio.apply_fill(
                decision.symbol,
                decision.side,
                decision.quantity,
                float(opportunity["entry_price"]),
                fee_rate=float(self.config.get("fee_rate", 0.001)),
            )
        except (KeyError, TypeError, ValueError) as error:
            await self.event_bus.publish("trade_rejected", {
                **opportunity, "rejection_reason": str(error)})
            return

        self._processed_order_ids.add(order_id)
        result = {
            **opportunity,
            "order_id": order_id,
            "risk_decision": decision.as_dict(),
            "portfolio": portfolio.snapshot(),
            "execution_mode": "paper",
            "order_status": "filled",
        }
        self.context.memory.add("paper_trade", result)
        await self.event_bus.publish("paper_fill", result)
