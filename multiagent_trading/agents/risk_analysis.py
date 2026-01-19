from multiagent_trading.agents.base import BaseAgent
import numpy as np

class RiskAnalysisAgent(BaseAgent):
    """
    Agente para análise de risco avançada, incluindo Monte Carlo e Value at Risk (VaR).
    """
    async def on_market_update(self, data):
        # Cálculo de VaR histórico simulado
        returns = np.random.normal(0.001, 0.02, 1000)
        var_95 = np.percentile(returns, 5)

        self.logger.info(f"Análise de Risco (VaR 95%): {var_95:.4f}")

        if var_95 < -0.05:
            self.logger.warning("Risco de cauda elevado detectado!")
            await self.event_bus.publish("risk_alert", {"type": "VaR", "value": var_95})

        # Simulação de Monte Carlo para projeção de 30 dias
        if hasattr(self.context.portfolio, "total_value"):
            projections = self.run_monte_carlo(self.context.portfolio.total_value, days=30)
            self.context.memory.add("risk_monte_carlo", {
                "median": float(np.median(projections[:, -1])),
                "worst_case": float(np.min(projections[:, -1])),
                "best_case": float(np.max(projections[:, -1]))
            })

    def run_monte_carlo(self, initial_value, days=30, simulations=100, mu=0.0005, sigma=0.01):
        """Executa simulações de Monte Carlo para projeção do valor do portfólio."""
        dt = 1
        projections = np.zeros((simulations, days))
        projections[:, 0] = initial_value

        for t in range(1, days):
            drift = (mu - 0.5 * sigma**2) * dt
            shock = sigma * np.sqrt(dt) * np.random.normal(0, 1, simulations)
            projections[:, t] = projections[:, t-1] * np.exp(drift + shock)

        return projections
