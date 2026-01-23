from multiagent_trading.agents.base import BaseAgent
import pandas as pd

class MultiTimeframeScannerAgent(BaseAgent):
    """
    Agente que analisa múltiplos períodos de tempo para confirmar tendências
    antes de gerar sinais de oportunidade.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tf_data = {} # {symbol: {tf: [prices]}}
        self.timeframes = self.config.get("timeframes", ["1m", "5m", "15m"])

    async def on_market_update(self, data):
        await super().on_market_update(data)
        symbol = data.get("symbol")
        if not symbol: return

        if symbol not in self.tf_data:
            self.tf_data[symbol] = {tf: [] for tf in self.timeframes}

        # Simulação de agregação de dados em diferentes timeframes
        # Em produção, viria do adaptador CCXT com múltiplos fetches
        price = data.get("close")
        for tf in self.timeframes:
            self.tf_data[symbol][tf].append(price)
            if len(self.tf_data[symbol][tf]) > 20:
                self.tf_data[symbol][tf].pop(0)

        # Verificar concordância de tendência (ex: todos acima da média)
        if self._all_timeframes_aligned(symbol):
            self.logger.info(f"Tendência multi-timeframe alinhada para {symbol}", tfs=self.timeframes)
            await self.event_bus.publish("opportunity_found", {
                "symbol": symbol,
                "side": "BUY",
                "strategy": "MULTI_TIMEFRAME"
            })

    def _all_timeframes_aligned(self, symbol):
        # Lógica simplificada: tendência de subida em todos os TFs ativos
        for tf in self.timeframes:
            prices = self.tf_data[symbol][tf]
            if len(prices) < 5: return False
            if prices[-1] <= prices[0]: return False # Não alinhado
        return True
