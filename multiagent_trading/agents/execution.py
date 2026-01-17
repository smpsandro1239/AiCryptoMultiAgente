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
        elif execution_type == "VWAP":
            await self.execute_vwap(opp)
        else:
            await self.execute_market(opp)

    async def execute_market(self, opp):
        symbol = opp["symbol"]
        side = opp["side"]
        usd_size = opp.get("optimized_size", 0)
        self.logger.info(f"{self.name} executing MARKET {side} for {symbol}, size in USD: {usd_size}")

        price = self.context.market_data.get(symbol, {}).get("close", 100)
        qty = usd_size / price if price > 0 else 0

        self.update_portfolio(symbol, side, qty, price)
        self.context.memory.add("execution", {"symbol": symbol, "side": side, "type": "MARKET", "price": price, "qty": qty})

    async def execute_twap(self, opp):
        symbol = opp["symbol"]
        side = opp["side"]
        total_usd_size = opp.get("optimized_size", 0)
        chunks = self.config.get("execution", {}).get("twap_chunks", 5)
        self.logger.info(f"{self.name} starting TWAP {side} for {symbol}, total size in USD: {total_usd_size}")

        usd_chunk = total_usd_size / chunks
        for i in range(chunks):
            price = self.context.market_data.get(symbol, {}).get("close", 100)
            qty_chunk = usd_chunk / price if price > 0 else 0
            self.update_portfolio(symbol, side, qty_chunk, price)
            await asyncio.sleep(0.01)
        self.context.memory.add("execution", {"symbol": symbol, "side": side, "type": "TWAP", "usd_size": total_usd_size})

    async def execute_vwap(self, opp):
        symbol = opp["symbol"]
        side = opp["side"]
        total_usd_size = opp.get("optimized_size", 0)
        self.logger.info(f"{self.name} starting VWAP {side} for {symbol}, total size in USD: {total_usd_size}")

        chunks = 5
        mock_volumes = [10, 20, 40, 20, 10]
        total_mock_vol = sum(mock_volumes)

        for i in range(chunks):
            v_factor = mock_volumes[i] / total_mock_vol
            usd_chunk = total_usd_size * v_factor
            price = self.context.market_data.get(symbol, {}).get("close", 100)
            qty_chunk = usd_chunk / price if price > 0 else 0
            self.logger.info(f"{self.name} VWAP chunk {i+1}/{chunks} (vol factor {v_factor:.2f})")
            self.update_portfolio(symbol, side, qty_chunk, price)
            await asyncio.sleep(0.01)

        self.context.memory.add("execution", {"symbol": symbol, "side": side, "type": "VWAP", "usd_size": total_usd_size})

    def update_portfolio(self, symbol, side, qty, price):
        if side == "BUY":
            cost = qty * price
            self.context.portfolio.update_balance(self.context.portfolio.base_currency, -cost)
            self.context.portfolio.update_position(symbol, qty)
        elif side == "SELL":
            # For simplicity, if we don't have enough qty, we sell what we have or short (depending on settings)
            # Here we just execute as requested
            self.context.portfolio.update_balance(self.context.portfolio.base_currency, qty * price)
            self.context.portfolio.update_position(symbol, -qty)
