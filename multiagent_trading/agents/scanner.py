from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.indicators.rsi import rsi
from multiagent_trading.indicators.ema import ema

class ScannerAgent(BaseAgent):
    async def on_market_update(self, data_batch):
        self.logger.info(f"{self.name} scanning for opportunities in {list(data_batch.keys())}...")

        if not hasattr(self, 'history'):
            self.history = {}

        for symbol, data in data_batch.items():
            price = data.get("close", 100)
            if symbol not in self.history:
                # Initialize with current price instead of hardcoded 100
                self.history[symbol] = [price] * 20

            self.history[symbol].append(price)
            if len(self.history[symbol]) > 100:
                self.history[symbol].pop(0)

            if len(self.history[symbol]) < 14:
                continue

            rsi_val = rsi(self.history[symbol], period=14)[-1]
            ema_val = ema(self.history[symbol], period=20)[-1]

            if rsi_val < 30 and price > ema_val:
                opportunity = {
                    "symbol": symbol,
                    "side": "BUY",
                    "reason": "RSI Oversold + Above EMA",
                    "price": price
                }
                await self.event_bus.publish("opportunity_found", opportunity)
            elif rsi_val > 70:
                opportunity = {
                    "symbol": symbol,
                    "side": "SELL",
                    "reason": "RSI Overbought",
                    "price": price
                }
                await self.event_bus.publish("opportunity_found", opportunity)
