from multiagent_trading.agents.base import BaseAgent

class RegimeAgent(BaseAgent):
    async def on_market_update(self, data):
        self.logger.info(f"{self.name} analyzing regime...")
        # Simulate logic: Trend following
        self.context.regime = "BULL"
        await self.event_bus.publish("regime_change", self.context.regime)
