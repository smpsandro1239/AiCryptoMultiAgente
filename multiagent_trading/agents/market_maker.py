from multiagent_trading.agents.base import BaseAgent
import random

class MarketMakerAgent(BaseAgent):
    """
    Agente que fornece liquidez colocando ordens limitadas (bids e asks)
    em torno do preço médio (mid-price).
    """
    async def on_market_update(self, data):
        mid_price = data.get("close")
        if not mid_price: return

        spread = 0.001 # 0.1% spread
        bid_price = mid_price * (1 - spread/2)
        ask_price = mid_price * (1 + spread/2)

        self.logger.info(f"Market Maker a colocar ordens para {data.get('symbol')}", bid=bid_price, ask=ask_price)

        await self.event_bus.publish("market_maker_orders", {
            "symbol": data.get("symbol"),
            "bid": bid_price,
            "ask": ask_price,
            "amount": 1.0
        })
