import asyncio
import itertools
import concurrent.futures
import multiprocessing

class BacktestOptimizer:
    """
    Otimiza parâmetros de agentes através de Grid Search durante o backtest.
    """
    def __init__(self, backtester_factory):
        self.backtester_factory = backtester_factory

    async def optimize(self, param_grid: dict, use_multiprocessing=True):
        """
        Executa múltiplos backtests de forma paralela para encontrar a melhor combinação de parâmetros.
        """
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

        if not use_multiprocessing:
            return await self._run_sequential(combinations)

        # Simulação de paralelização asíncrona
        # (Em ambiente real usaria multiprocessing.Pool ou similar com Backtester serializável)
        tasks = [self._run_single_backtest(combo) for combo in combinations]
        results = await asyncio.gather(*tasks)

        # Ordenar pelo melhor Sharpe Ratio
        results.sort(key=lambda x: x["sharpe"], reverse=True)
        return results

    async def _run_single_backtest(self, combo):
        bt = self.backtester_factory(combo)
        bt_res = await bt.run()
        return {
            "params": combo,
            "sharpe": bt_res["metrics"]["sharpe_ratio"],
            "final_value": bt_res["metrics"]["final_value"]
        }

    async def _run_sequential(self, combinations):
        results = []
        for combo in combinations:
            res = await self._run_single_backtest(combo)
            results.append(res)
        results.sort(key=lambda x: x["sharpe"], reverse=True)
        return results
