from multiagent_trading.agents.base import BaseAgent

class SupervisorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)
        self.event_bus.subscribe("reasoning_complete", self.on_reasoning_complete)

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} a solicitar raciocínio IA para {opp['symbol']}...")
        await self.event_bus.publish("request_reasoning", opp)

    async def on_reasoning_complete(self, opp):
        self.logger.info(f"{self.name} a aprovar negociação com base no raciocínio IA para {opp['symbol']}...")
        await self.event_bus.publish("trade_approved", opp)
