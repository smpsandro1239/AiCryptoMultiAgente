from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.indicators.rsi import rsi
from multiagent_trading.indicators.ema import ema

class ScannerAgent(BaseAgent):
    async def on_market_update(self, data):
        self.logger.info(f"{self.name} scanning for opportunities...")

        # In a real scenario, context.market_data would be a list of historical data
        # for multiple symbols. For this example, we'll assume we have closing prices.
        # Let's mock a bit of history from the current tick to make indicators work.
        closes = self.context.config.get("mock_history", [100, 102, 101, 103, 105, 107, 106, 108, 110])
        closes.append(data.get("close", 110))

        rsi_val = rsi(closes, period=7)[-1]
        ema_val = ema(closes, period=5)[-1]

        self.logger.info(f"RSI: {rsi_val:.2f}, EMA: {ema_val:.2f}")

        # Simple Mean Reversion logic
        if rsi_val < 30:
            opportunity = {"symbol": data.get("symbol", "BTC/USDT"), "side": "BUY", "reason": "RSI Oversold"}
            await self.event_bus.publish("opportunity_found", opportunity)
        elif rsi_val > 70:
            opportunity = {"symbol": data.get("symbol", "BTC/USDT"), "side": "SELL", "reason": "RSI Overbought"}
            await self.event_bus.publish("opportunity_found", opportunity)

        # Simple Trend Following logic
        elif data.get("close", 0) > ema_val:
            opportunity = {"symbol": data.get("symbol", "BTC/USDT"), "side": "BUY", "reason": "Price above EMA"}
            await self.event_bus.publish("opportunity_found", opportunity)
