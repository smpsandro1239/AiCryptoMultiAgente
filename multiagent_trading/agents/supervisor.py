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
        self.reputation_scores = {} # {agent_name: score}

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} a solicitar raciocínio IA para {opp['symbol']}...")
        await self.event_bus.publish("request_reasoning", opp)

    async def on_reasoning_complete(self, opp):
        opp_id = f"{opp['symbol']}_{opp.get('side')}"
        agent_name = opp.get("agent", "UNKNOWN")

        if opp_id not in self.votes:
            self.votes[opp_id] = []

        # Sistema de Reputação: Agentes com maior score têm votos que valem mais
        # (Lógica simplificada para demonstração)
        score = self.reputation_scores.get(agent_name, 1.0)
        self.votes[opp_id].append({"agent": agent_name, "weight": score})

        total_weight = sum(v["weight"] for v in self.votes[opp_id])

        if total_weight >= self.required_votes:
            self.logger.info(f"{self.name} a aprovar negociação (peso total: {total_weight:.2f}) para {opp['symbol']}...")
            await self.event_bus.publish("trade_approved", opp)

            # Incrementar reputação do agente proponente
            self.reputation_scores[agent_name] = score + 0.1
            del self.votes[opp_id]
        else:
            self.logger.info(f"{self.name} a aguardar mais peso de votos para {opp['symbol']} (atual: {total_weight:.2f})")
