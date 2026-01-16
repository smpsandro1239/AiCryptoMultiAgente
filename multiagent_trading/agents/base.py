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

class RegimeAgent(BaseAgent):
    async def on_market_update(self, data):
        self.logger.info(f"{self.name} analyzing regime...")
        self.context.regime = "BULL" # Placeholder logic
        await self.event_bus.publish("regime_change", self.context.regime)

class ScannerAgent(BaseAgent):
    async def on_market_update(self, data):
        self.logger.info(f"{self.name} scanning for opportunities...")
        opportunity = {"symbol": "BTC/USDT", "side": "BUY"}
        await self.event_bus.publish("opportunity_found", opportunity)

class RiskAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opp):
        self.logger.info(f"{self.name} assessing risk for {opp['symbol']}...")
        opp["risk_ok"] = True
        await self.event_bus.publish("risk_assessed", opp)

class SupervisorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} approving trade for {opp['symbol']}...")
        await self.event_bus.publish("trade_approved", opp)

class ExecutionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)

    async def on_trade_approved(self, opp):
        self.logger.info(f"{self.name} executing trade for {opp['symbol']}...")
        # Update portfolio
        self.context.portfolio.total_value += 10 # Simulate profit
        self.context.memory.add("trade", opp)
