class BaseAgent:
    def __init__(self, name, config, context, event_bus, logger):
        self.name = name
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.logger = logger
        self.event_bus.subscribe("market_update", self.on_market_update)

    async def on_market_update(self, data):
        pass
