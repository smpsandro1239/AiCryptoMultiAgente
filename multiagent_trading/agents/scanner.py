from multiagent_trading.agents.base import BaseAgent

class ScannerAgent(BaseAgent):
    async def on_market_update(self, data):
        self.logger.info(f"{self.name} a procurar oportunidades...", symbol=data.get("symbol"))
        opportunity = {"symbol": data.get("symbol", "BTC/USDT"), "side": "BUY"}
        await self.event_bus.publish("opportunity_found", opportunity)
