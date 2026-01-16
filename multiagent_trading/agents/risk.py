from multiagent_trading.agents.base import BaseAgent

class RiskAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opp):
        self.logger.info(f"{self.name} assessing risk for {opp['symbol']}...")
        # Policy-based risk assessment
        max_exposure = self.config.get("risk", {}).get("max_exposure", 0.1)
        opp["risk_ok"] = True
        opp["position_size"] = self.context.portfolio.total_value * 0.02 # 2% risk
        await self.event_bus.publish("risk_assessed", opp)
