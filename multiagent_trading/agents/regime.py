from multiagent_trading.agents.base import BaseAgent

class RegimeAgent(BaseAgent):
    async def on_market_update(self, data):
        self.logger.info(f"{self.name} a analisar o regime...", symbol=data.get("symbol"))
        self.context.regime = "BULL" # Placeholder logic
        await self.event_bus.publish("regime_change", self.context.regime)
