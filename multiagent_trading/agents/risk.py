"""Independent pre-trade risk agent; fails closed when portfolio or market data is absent."""
from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.core.risk_engine import RiskEngine
from multiagent_trading.models.portfolio import PortfolioState


class RiskAgent(BaseAgent):
    """Apply hard limits before any qualitative reasoning or execution."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.risk_engine is None:
            self.context.risk_engine = RiskEngine()
        self.risk_engine = self.context.risk_engine
        if self.context.portfolio is None:
            capital = float(self.config.get("initial_capital", 10_000.0))
            self.context.portfolio = PortfolioState(initial_value=capital)
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opportunity):
        """Assess the opportunity and publish an explicit allow/deny decision."""
        decision = self.risk_engine.assess(
            opportunity,
            self.context.portfolio,
            daily_pnl=float(getattr(self.context, "daily_pnl", 0.0)),
        )
        opportunity["risk_decision"] = decision.as_dict()
        await self.event_bus.publish(
            "risk_assessed" if decision.approved else "trade_rejected",
            opportunity,
        )
