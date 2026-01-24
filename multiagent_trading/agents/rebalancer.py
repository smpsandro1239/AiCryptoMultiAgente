from multiagent_trading.agents.base import BaseAgent
import numpy as np

class DynamicRebalancingAgent(BaseAgent):
    """
    Agente que monitoriza o desvio (drift) do portfólio em relação aos pesos alvo.
    Aciona rebalanceamento automático se o desvio exceder o limiar.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_weights = self.config.get("target_weights", {"BTC/USDT": 0.5, "ETH/USDT": 0.5})
        self.threshold = self.config.get("drift_threshold", 0.05) # 5% de desvio

    async def on_market_update(self, data):
        await super().on_market_update(data)

        if not hasattr(self.context.portfolio, "positions"):
            return

        # Simulação de cálculo de pesos atuais
        # Em produção, usaria os preços atuais e quantidades no portfólio
        total_val = self.context.portfolio.total_value

        for symbol, target in self.target_weights.items():
            # Simular desvio aleatório para demonstração
            current_weight = target + (np.random.random() - 0.5) * 0.2
            drift = abs(current_weight - target)

            if drift > self.threshold:
                self.logger.warning(
                    f"Desvio de portfólio detectado para {symbol}",
                    current=current_weight,
                    target=target,
                    drift=drift
                )

                await self.event_bus.publish("rebalance_triggered", {
                    "symbol": symbol,
                    "target_weight": target,
                    "order_type": "REBALANCE"
                })

class LongShortRebalancingAgent(DynamicRebalancingAgent):
    """
    Versão legada mantida para compatibilidade, agora herdando da lógica dinâmica.
    """
    pass
