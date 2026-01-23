from multiagent_trading.agents.base import BaseAgent

class LLMAgent(BaseAgent):
    """
    Agente que fornece raciocínio qualitativo para decisões de trading.
    Agora com suporte para RAG (Retrieval-Augmented Generation).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.knowledge_base = [
            "O Bitcoin tende a subir em ambientes de taxas de juro baixas.",
            "O Ethereum tem forte correlação com o volume de transações DeFi.",
            "Regimes de alta volatilidade favorecem estratégias de Scalping.",
            "A análise de microestrutura sugere reversões quando o imbalance excede 0.8."
        ]
        self.event_bus.subscribe("request_reasoning", self.on_request_reasoning)

    async def _query_rag(self, query):
        """Simulação de busca semântica (RAG)."""
        # Procura por palavras-chave na base de conhecimentos
        results = [k for k in self.knowledge_base if any(w.lower() in k.lower() for w in query.split())]
        return results if results else ["Nenhuma informação específica encontrada no research."]

    async def on_request_reasoning(self, opp):
        self.logger.info(f"LLM a gerar raciocínio para {opp['symbol']}...")

        # Simulação de análise qualitativa baseada no contexto
        regime = self.context.regime or "desconhecido"
        side = opp.get("side")

        # Consultar base de conhecimentos (RAG)
        context_docs = await self._query_rag(f"{opp['symbol']} {opp.get('strategy', '')}")
        research_note = context_docs[0] if context_docs else ""

        rationale = (
            f"Análise Qualitativa: A posição de {side} em {opp['symbol']} "
            f"é recomendada no regime {regime}. "
            f"Nota de Research: {research_note} "
            f"Os indicadores técnicos confirmam a força do movimento."
        )

        opp["rationale"] = rationale
        self.logger.info("Raciocínio concluído", rationale=rationale)
        await self.event_bus.publish("reasoning_complete", opp)
