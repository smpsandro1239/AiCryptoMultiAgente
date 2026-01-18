import numpy as np
from multiagent_trading.agents.base import BaseAgent

class MVOOptimizerAgent(BaseAgent):
    """
    Otimizador de Média-Variância (Mean-Variance Optimization).
    Calcula pesos ótimos para o portfólio baseando-se no retorno esperado e covariância.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asset_history = {} # symbol: list of returns
        self.risk_aversion = self.config.get("mvo", {}).get("risk_aversion", 1.0)

    async def on_market_update(self, data_batch):
        # Atualizar histórico de retornos para todos os ativos
        for symbol, data in data_batch.items():
            if symbol not in self.asset_history:
                self.asset_history[symbol] = []

            if not hasattr(self, 'last_prices'): self.last_prices = {}

            current_price = data.get("close", 0)
            if symbol in self.last_prices and self.last_prices[symbol] > 0:
                ret = (current_price - self.last_prices[symbol]) / self.last_prices[symbol]
                self.asset_history[symbol].append(ret)

            self.last_prices[symbol] = current_price

            if len(self.asset_history[symbol]) > 50:
                self.asset_history[symbol].pop(0)

        # Se tivermos dados suficientes, recalculamos a alocação ótima
        symbols = list(self.asset_history.keys())
        if len(symbols) >= 2 and all(len(h) >= 20 for h in self.asset_history.values()):
            self.optimize_portfolio(symbols)

    def optimize_portfolio(self, symbols):
        self.logger.info(f"{self.name} a calcular pesos ótimos via MVO...")

        returns_matrix = np.array([self.asset_history[s][-20:] for s in symbols])
        mean_returns = np.mean(returns_matrix, axis=1)
        cov_matrix = np.cov(returns_matrix)

        # Simplificação: Markowitz sem restrições complexas (analytical solution snippet)
        # w = (1/gamma) * inv(Sigma) * mu
        try:
            inv_cov = np.linalg.inv(cov_matrix + np.eye(len(symbols)) * 1e-6) # Regularization
            weights = (1.0 / self.risk_aversion) * np.dot(inv_cov, mean_returns)

            # Normalizar para que a soma dos pesos não exceda 1.0 (ou usar o valor absoluto para long/short)
            sum_w = np.sum(np.abs(weights))
            if sum_w > 0:
                weights = weights / sum_w

            optimal_weights = {s: float(w) for s, w in zip(symbols, weights)}
            self.logger.info(f"Pesos ótimos MVO: {optimal_weights}")

            # Guardar pesos no contexto para o RebalancerAgent
            if not hasattr(self.context, 'mvo_weights'):
                self.context.mvo_weights = {}
            self.context.mvo_weights = optimal_weights

        except np.linalg.LinAlgError:
            self.logger.warning(f"{self.name}: Erro ao inverter matriz de covariância.")
