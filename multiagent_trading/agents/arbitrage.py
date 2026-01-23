from multiagent_trading.agents.base import BaseAgent
import random

class ArbitrageAgent(BaseAgent):
    """
    Agente que identifica discrepâncias de preços entre diferentes exchanges (mock).
    """
    async def on_market_update(self, data):
        await super().on_market_update(data)
        symbol = data.get("symbol")
        price_ex_a = data.get("close", 100)

        # Simulação de preço noutra exchange
        price_ex_b = price_ex_a * random.uniform(0.99, 1.01)

        spread = abs(price_ex_a - price_ex_b) / min(price_ex_a, price_ex_b)

        if spread > 0.005: # Spread de 0.5%
            side = "BUY_A_SELL_B" if price_ex_a < price_ex_b else "BUY_B_SELL_A"
            self.logger.info(f"Oportunidade de Arbitragem detetada para {symbol}", spread=spread, side=side)

            await self.event_bus.publish("opportunity_found", {
                "symbol": symbol,
                "side": side,
                "strategy": "ARBITRAGE",
                "spread": spread
            })
