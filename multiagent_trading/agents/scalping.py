from multiagent_trading.agents.base import BaseAgent
import numpy as np

class ScalpingAgent(BaseAgent):
    """
    Agente focado em estratégias de alta frequência, monitorizando micro-momentum.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prices = []

    async def on_market_update(self, data):
        self.prices.append(data.get("close"))
        if len(self.prices) > 10: self.prices.pop(0)

        if len(self.prices) < 5: return

        # Micro-momentum simples
        momentum = (self.prices[-1] - self.prices[-5]) / self.prices[-5]

        if abs(momentum) > 0.001: # 0.1% movimento rápido
            side = "BUY" if momentum > 0 else "SELL"
            self.logger.info(f"Sinal de Scalping detetado para {data.get('symbol')}", momentum=momentum, side=side)

            await self.event_bus.publish("opportunity_found", {
                "symbol": data.get("symbol"),
                "side": side,
                "strategy": "SCALPING"
            })
