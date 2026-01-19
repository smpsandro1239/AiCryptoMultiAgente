from multiagent_trading.agents.base import BaseAgent

class RiskAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opp):
        self.logger.info(f"{self.name} a avaliar risco para {opp['symbol']}...")
        opp["risk_ok"] = True
        await self.event_bus.publish("risk_assessed", opp)
