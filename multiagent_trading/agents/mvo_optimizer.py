from multiagent_trading.agents.base import BaseAgent
import numpy as np
from scipy.optimize import minimize

class MVOOptimizerAgent(BaseAgent):
    """
    Agente que utiliza Mean-Variance Optimization (Markowitz) para alocação de capital.
    Calcula pesos ótimos baseados em retornos esperados e covariância.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.risk_aversion = self.config.get("risk_aversion", 1.0)
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opp):
        self.logger.info(f"{self.name} a otimizar portfólio via MVO para {opp['symbol']}...")

        # Simulação de retornos e covariância (em cenário real viria de dados históricos)
        symbols = [opp['symbol'], "ETH/USDT", "SOL/USDT"]
        returns = np.array([0.05, 0.04, 0.06])
        cov_matrix = np.array([
            [0.0004, 0.0002, 0.0001],
            [0.0002, 0.0003, 0.00015],
            [0.0001, 0.00015, 0.0005]
        ])

        num_assets = len(symbols)

        def objective(weights):
            port_return = np.dot(weights, returns)
            port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -(port_return - 0.5 * self.risk_aversion * port_vol**2)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_weights = num_assets * [1. / num_assets]

        result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

        if result.success:
            optimal_weights = dict(zip(symbols, result.x))
            opp["optimal_weight"] = optimal_weights.get(opp['symbol'], 0)
            self.logger.info(f"Otimização MVO concluída para {opp['symbol']}", weight=opp["optimal_weight"])
            await self.event_bus.publish("allocation_optimized", opp)
        else:
            self.logger.error("Falha na otimização MVO")
