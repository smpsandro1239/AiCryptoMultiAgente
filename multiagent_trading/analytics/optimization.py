import asyncio
import itertools

class BacktestOptimizer:
    """
    Otimiza parâmetros de agentes através de Grid Search durante o backtest.
    """
    def __init__(self, backtester_factory):
        self.backtester_factory = backtester_factory

    async def optimize(self, param_grid: dict):
        """
        Executa múltiplos backtests para encontrar a melhor combinação de parâmetros.
        param_grid: {"risk_aversion": [1.0, 2.0], "stop_loss_pct": [0.02, 0.05]}
        """
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

        results = []
        for combo in combinations:
            print(f"A testar combinação: {combo}")
            # Em produção, usaria multiprocessing para acelerar
            bt = self.backtester_factory(combo)
            bt_res = await bt.run()

            results.append({
                "params": combo,
                "sharpe": bt_res["metrics"]["sharpe_ratio"],
                "final_value": bt_res["metrics"]["final_value"]
            })

        # Ordenar pelo melhor Sharpe Ratio
        results.sort(key=lambda x: x["sharpe"], reverse=True)
        return results
