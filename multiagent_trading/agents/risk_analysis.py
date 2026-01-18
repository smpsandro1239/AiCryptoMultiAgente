import numpy as np
from multiagent_trading.agents.base import BaseAgent

class RiskAnalysisAgent(BaseAgent):
    """
    Performs advanced risk modeling, including Monte Carlo simulations and Value at Risk (VaR) calculations.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_simulations = self.config.get("risk_analysis", {}).get("simulations", 1000)
        self.confidence_level = self.config.get("risk_analysis", {}).get("confidence", 0.95)

    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        # We need historical returns for VaR calculation
        symbol = next(iter(data_batch))
        if not hasattr(self, 'prices'): self.prices = []
        self.prices.append(data_batch[symbol].get("close", 100))

        if len(self.prices) < 30: # Need enough data
            return

        returns = np.diff(self.prices) / self.prices[:-1]

        # 1. Historical VaR
        var_hist = np.percentile(returns, (1 - self.confidence_level) * 100)

        # 2. Monte Carlo Simulation for future price paths
        last_price = self.prices[-1]
        mu = np.mean(returns)
        sigma = np.std(returns)

        # Simulate 10 steps ahead for 1000 scenarios
        horizon = 10
        sim_results = []
        for _ in range(self.num_simulations):
            path = [last_price]
            for _ in range(horizon):
                next_p = path[-1] * (1 + np.random.normal(mu, sigma))
                path.append(next_p)
            sim_results.append(path[-1])

        var_mc = (np.percentile(sim_results, (1 - self.confidence_level) * 100) - last_price) / last_price

        self.logger.info(f"{self.name} Risk Report for {symbol}: Hist VaR={var_hist:.2%}, MC VaR={var_mc:.2%}")

        analysis = {
            "symbol": symbol,
            "var_historical": var_hist,
            "var_monte_carlo": var_mc,
            "mu": mu,
            "sigma": sigma,
            "sim_final_prices": sim_results
        }

        self.context.memory.add("risk_analysis", analysis)
        await self.event_bus.publish("risk_analysis_complete", analysis)
