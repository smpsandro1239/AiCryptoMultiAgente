from multiagent_trading.agents.base import BaseAgent

class LLMAgent(BaseAgent):
    """
    Agente que fornece raciocínio qualitativo para decisões de trading.
    Acionado pelo SupervisorAgent via evento 'request_reasoning'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("request_reasoning", self.on_request_reasoning)

    async def on_request_reasoning(self, opp):
        self.logger.info(f"LLM a gerar raciocínio para {opp['symbol']}...")

        # Simulação de análise qualitativa baseada no contexto
        regime = self.context.regime or "desconhecido"
        side = opp.get("side")

        rationale = (
            f"A análise qualitativa sugere que a posição de {side} em {opp['symbol']} "
            f"é favorável dado o regime de mercado {regime}. "
            f"Os indicadores técnicos estão alinhados com o momentum atual."
        )

        opp["rationale"] = rationale
        self.logger.info("Raciocínio concluído", rationale=rationale)
        await self.event_bus.publish("reasoning_complete", opp)
