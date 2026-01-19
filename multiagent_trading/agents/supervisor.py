from multiagent_trading.agents.base import BaseAgent

class SupervisorAgent(BaseAgent):
    """
    Agente que coordena a aprovação final de trocas, agora suportando
    lógica de votação em ensemble de múltiplos agentes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)
        self.event_bus.subscribe("reasoning_complete", self.on_reasoning_complete)
        self.votes = {} # {opp_id: [votes]}
        self.required_votes = self.config.get("required_votes", 1)

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} a solicitar raciocínio IA para {opp['symbol']}...")
        await self.event_bus.publish("request_reasoning", opp)

    async def on_reasoning_complete(self, opp):
        opp_id = f"{opp['symbol']}_{opp.get('side')}"
        if opp_id not in self.votes:
            self.votes[opp_id] = []

        self.votes[opp_id].append("AI_REASONING")

        if len(self.votes[opp_id]) >= self.required_votes:
            self.logger.info(f"{self.name} a aprovar negociação (votos: {self.votes[opp_id]}) para {opp['symbol']}...")
            await self.event_bus.publish("trade_approved", opp)
            del self.votes[opp_id]
        else:
            self.logger.info(f"{self.name} a aguardar mais votos para {opp['symbol']}...")
