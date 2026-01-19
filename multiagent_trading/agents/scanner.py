from multiagent_trading.agents.base import BaseAgent

class ScannerAgent(BaseAgent):
    async def on_market_update(self, data):
        # Suporte para dados multi-símbolo
        if "symbol" in data:
            # Dado único
            await self._scan_symbol(data.get("symbol"), data)
        else:
            # Dicionário de símbolos {symbol: tick_data}
            for symbol, tick_data in data.items():
                if isinstance(tick_data, dict):
                    await self._scan_symbol(symbol, tick_data)

    async def _scan_symbol(self, symbol, tick_data):
        self.logger.info(f"{self.name} a procurar oportunidades para {symbol}...")
        # Lógica de scan (simplificada)
        opportunity = {"symbol": symbol, "side": "BUY", "price": tick_data.get("close")}
        await self.event_bus.publish("opportunity_found", opportunity)
