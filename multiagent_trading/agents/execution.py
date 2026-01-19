from multiagent_trading.agents.base import BaseAgent

class ExecutionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)

    async def on_trade_approved(self, opp):
        self.logger.info(f"{self.name} a executar negociação para {opp['symbol']}...")
        # Atualizar portfólio
        self.context.portfolio.total_value += 10 # Simular lucro
        self.context.memory.add("trade", opp)
