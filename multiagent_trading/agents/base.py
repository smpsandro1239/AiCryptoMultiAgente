import time

class BaseAgent:
    def __init__(self, name, config, context, event_bus, logger):
        self.name = name
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.logger = logger
        self.last_heartbeat = time.time()
        self.event_bus.subscribe("market_update", self.on_market_update)

    async def on_market_update(self, data):
        """Método base para processar atualizações de mercado. Deve ser chamado via super()."""
        self.heartbeat()

    def heartbeat(self):
        """Atualiza o timestamp da última atividade do agente."""
        self.last_heartbeat = time.time()
