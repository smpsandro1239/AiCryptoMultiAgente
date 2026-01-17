from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.indicators.macd import macd
from multiagent_trading.indicators.rsi import rsi

class RegimeAgent(BaseAgent):
    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        # Use the first available symbol for regime analysis (usually a major like BTC)
        symbol = next(iter(data_batch))

        if not hasattr(self, 'history'):
            self.history = []

        self.history.append(data_batch[symbol].get("close", 100))
        if len(self.history) > 100:
            self.history.pop(0)

        if len(self.history) < 26: # Need enough data for MACD
            return

        macd_line, signal_line, hist = macd(self.history)
        rsi_val = rsi(self.history, period=14)[-1]

        current_macd = macd_line[-1]
        current_signal = signal_line[-1]

        if current_macd > current_signal and rsi_val > 50:
            new_regime = "BULL"
        elif current_macd < current_signal and rsi_val < 50:
            new_regime = "BEAR"
        else:
            new_regime = "SIDEWAYS"

        if new_regime != self.context.regime:
            self.logger.info(f"{self.name} regime change: {self.context.regime} -> {new_regime}")
            self.context.regime = new_regime
            await self.event_bus.publish("regime_change", new_regime)
