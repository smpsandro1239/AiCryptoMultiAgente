from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.indicators.rsi import rsi
from multiagent_trading.indicators.ema import ema

class ScannerAgent(BaseAgent):
    async def on_market_update(self, data_batch):
        """
        data_batch: { symbol: {close, ...} }
        """
        self.logger.info(f"{self.name} scanning for opportunities in {list(data_batch.keys())}...")

        # Maintain local history per symbol for indicator calculation
        if not hasattr(self, 'history'):
            self.history = {}

        for symbol, data in data_batch.items():
            if symbol not in self.history:
                self.history[symbol] = [100.0] * 20 # Mock initial history

            self.history[symbol].append(data.get("close", 100))
            if len(self.history[symbol]) > 100:
                self.history[symbol].pop(0)

            # Indicator logic
            rsi_val = rsi(self.history[symbol], period=14)[-1]
            ema_val = ema(self.history[symbol], period=20)[-1]

            # Simple combined logic
            if rsi_val < 30 and data.get("close") > ema_val:
                opportunity = {
                    "symbol": symbol,
                    "side": "BUY",
                    "reason": "RSI Oversold + Above EMA",
                    "price": data.get("close")
                }
                await self.event_bus.publish("opportunity_found", opportunity)
            elif rsi_val > 70:
                opportunity = {
                    "symbol": symbol,
                    "side": "SELL",
                    "reason": "RSI Overbought",
                    "price": data.get("close")
                }
                await self.event_bus.publish("opportunity_found", opportunity)
