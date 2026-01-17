from multiagent_trading.agents.base import BaseAgent

class PortfolioOptimizerAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} optimizing allocation for {opp['symbol']}...")

        # Simple allocation logic:
        # Don't allocate more than 20% of total portfolio to a single trade
        max_allocation = self.context.portfolio.total_value * 0.2
        requested_size = opp.get("position_size", 0)

        opp["optimized_size"] = min(requested_size, max_allocation)

        # Check if we have enough base currency balance
        base_balance = self.context.portfolio.balances.get(self.context.portfolio.base_currency, 0.0)
        if base_balance < opp["optimized_size"]:
            opp["optimized_size"] = base_balance

        await self.event_bus.publish("allocation_optimized", opp)
