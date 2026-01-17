from multiagent_trading.agents.base import BaseAgent

class SupervisorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("allocation_optimized", self.on_allocation_optimized)
        self.event_bus.subscribe("reasoning_complete", self.on_reasoning_complete)

    async def on_allocation_optimized(self, opp):
        self.logger.info(f"{self.name} requesting AI reasoning for {opp['symbol']}...")
        if opp.get("optimized_size", 0) > 0:
            # Instead of approving directly, request qualitative reasoning
            await self.event_bus.publish("request_reasoning", opp)
        else:
            self.logger.warning(f"{self.name} rejected trade for {opp['symbol']} due to zero allocation.")

    async def on_reasoning_complete(self, opp):
        self.logger.info(f"{self.name} final approval for {opp['symbol']} with AI rationale...")
        await self.event_bus.publish("trade_approved", opp)
