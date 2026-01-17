import numpy as np
from multiagent_trading.agents.base import BaseAgent

class RiskParityOptimizerAgent(BaseAgent):
    """
    Allocates capital based on Risk Parity (inverse of volatility).
    Assets with higher volatility get lower allocation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)
        self.volatilities = {} # symbol: rolling_vol

    async def on_market_update(self, data_batch):
        # Update volatilities for risk parity calculation
        for symbol, data in data_batch.items():
            if not hasattr(self, 'prices'): self.prices = {}
            if symbol not in self.prices: self.prices[symbol] = []

            self.prices[symbol].append(data.get("close", 100))
            if len(self.prices[symbol]) > 20:
                self.prices[symbol].pop(0)
                returns = np.diff(self.prices[symbol]) / self.prices[symbol][:-1]
                self.volatilities[symbol] = np.std(returns)

    async def on_risk_assessed(self, opp):
        symbol = opp['symbol']
        self.logger.info(f"{self.name} optimizing allocation for {symbol} using Risk Parity...")

        # Calculate inverse volatility weight
        vol = self.volatilities.get(symbol, 0.01) # fallback
        if vol == 0: vol = 0.01

        # Risk Parity weight: w_i = (1/vol_i) / sum(1/vol_j)
        # Simplified for a single trade against total potential:
        inv_vol = 1.0 / vol

        # Total sum of inv_vol for all symbols (mocked for this trade instance)
        total_inv_vol = sum([1.0/v if v > 0 else 100 for v in self.volatilities.values()]) or inv_vol

        weight = inv_vol / total_inv_vol

        # Max allocation: 25% of portfolio * risk parity weight
        max_alloc = self.context.portfolio.total_value * 0.25 * weight

        opp["optimized_size"] = min(opp.get("position_size", max_alloc), max_alloc)

        await self.event_bus.publish("allocation_optimized", opp)
