from multiagent_trading.agents.base import BaseAgent

class RiskAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opp):
        self.logger.info(f"{self.name} assessing risk for {opp['symbol']}...")

        # Determine position size as 1% of portfolio value
        opp["risk_ok"] = True
        opp["position_size"] = self.context.portfolio.total_value * 0.01

        await self.event_bus.publish("risk_assessed", opp)
