from multiagent_trading.agents.base import BaseAgent

class SupervisorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} a aprovar negociação para {opp['symbol']}...")
        await self.event_bus.publish("trade_approved", opp)
