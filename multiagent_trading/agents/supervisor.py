from multiagent_trading.agents.base import BaseAgent

class SupervisorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Now subscribes to optimizer instead of risk
        self.event_bus.subscribe("allocation_optimized", self.on_allocation_optimized)

    async def on_allocation_optimized(self, opp):
        self.logger.info(f"{self.name} final approval for {opp['symbol']} with size {opp.get('optimized_size')}...")
        if opp.get("optimized_size", 0) > 0:
            await self.event_bus.publish("trade_approved", opp)
        else:
            self.logger.warning(f"{self.name} rejected trade for {opp['symbol']} due to zero allocation.")
