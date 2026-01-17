import asyncio
from multiagent_trading.agents.base import BaseAgent

class MarketMakerAgent(BaseAgent):
    """
    Simulates a Market Maker agent that provides liquidity by placing limit orders.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spread = self.config.get("market_making", {}).get("spread", 0.0002)

    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        self.logger.info(f"{self.name} quoting market prices...")

        for symbol, data in data_batch.items():
            mid_price = data.get("close", 100)
            bid = mid_price * (1 - self.spread/2)
            ask = mid_price * (1 + self.spread/2)

            self.logger.info(f"Quotes for {symbol}: Bid {bid:.2f}, Ask {ask:.2f}")

            # In a real HFT scenario, these would be limit orders.
            # Here we just log the activity.
            self.context.memory.add("mm_quote", {"symbol": symbol, "bid": bid, "ask": ask})
