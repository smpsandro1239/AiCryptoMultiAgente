from multiagent_trading.agents.base import BaseAgent

class LongShortRebalancingAgent(BaseAgent):
    """
    Agente que mantém pesos alvo no portfólio, suportando estratégias Long/Short.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_weights = self.config.get("target_weights", {}) # {"BTC/USDT": 0.5, "ETH/USDT": -0.2}

    async def on_market_update(self, data):
        await super().on_market_update(data)
        # Lógica de rebalanceamento periódico
        # Em produção, verificaria o desvio dos pesos atuais e geraria ordens
        if self.target_weights:
            self.logger.info(f"A verificar rebalanceamento para {list(self.target_weights.keys())}")
            # Publicar sinal de rebalanceamento (simulado)
            # await self.event_bus.publish("rebalance_required", self.target_weights)
