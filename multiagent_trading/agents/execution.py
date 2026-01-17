import asyncio
from multiagent_trading.agents.base import BaseAgent

class ExecutionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)

    async def on_trade_approved(self, opp):
        execution_type = self.config.get("execution", {}).get("type", "MARKET")

        if execution_type == "TWAP":
            await self.execute_twap(opp)
        else:
            await self.execute_market(opp)

    async def execute_market(self, opp):
        symbol = opp["symbol"]
        side = opp["side"]
        size = opp.get("optimized_size", 0)

        self.logger.info(f"{self.name} executing MARKET {side} for {symbol}, size: {size}")

        # Simulate execution
        price = self.context.market_data.get(symbol, {}).get("close", 100)
        self.update_portfolio(symbol, side, size, price)

        self.context.memory.add("execution", {"symbol": symbol, "side": side, "type": "MARKET", "price": price})

    async def execute_twap(self, opp):
        symbol = opp["symbol"]
        side = opp["side"]
        total_size = opp.get("optimized_size", 0)
        chunks = self.config.get("execution", {}).get("twap_chunks", 5)

        self.logger.info(f"{self.name} starting TWAP {side} for {symbol}, total size: {total_size} in {chunks} chunks")

        chunk_size = total_size / chunks
        for i in range(chunks):
            price = self.context.market_data.get(symbol, {}).get("close", 100)
            self.logger.info(f"{self.name} TWAP chunk {i+1}/{chunks} for {symbol}")
            self.update_portfolio(symbol, side, chunk_size, price)
            await asyncio.sleep(0.1) # Short delay for simulation

        self.context.memory.add("execution", {"symbol": symbol, "side": side, "type": "TWAP", "size": total_size})

    def update_portfolio(self, symbol, side, size, price):
        if side == "BUY":
            cost = size * price
            self.context.portfolio.update_balance(self.context.portfolio.base_currency, -cost)
            self.context.portfolio.update_position(symbol, size)
        elif side == "SELL":
            # For simplicity, assume selling the whole position or the requested size
            self.context.portfolio.update_balance(self.context.portfolio.base_currency, size * price)
            self.context.portfolio.update_position(symbol, -size)
