"""Supervisor that cannot approve a trade without an explicit risk decision."""
from multiagent_trading.agents.base import BaseAgent


class SupervisorAgent(BaseAgent):
    """Coordinates reasoning only after an independent risk approval."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)
        self.event_bus.subscribe("reasoning_complete", self.on_reasoning_complete)

    async def on_risk_assessed(self, opportunity):
        decision = opportunity.get("risk_decision")
        if not isinstance(decision, dict) or decision.get("approved") is not True:
            await self.event_bus.publish("trade_rejected", opportunity)
            return
        await self.event_bus.publish("request_reasoning", opportunity)

    async def on_reasoning_complete(self, opportunity):
        decision = opportunity.get("risk_decision")
        if not isinstance(decision, dict) or decision.get("approved") is not True:
            await self.event_bus.publish("trade_rejected", opportunity)
            return
        await self.event_bus.publish("trade_approved", opportunity)
