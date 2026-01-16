from multiagent_trading.agents.base import BaseAgent

class ExecutionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)

    async def on_trade_approved(self, opp):
        symbol = opp["symbol"]
        side = opp["side"]
        self.logger.info(f"{self.name} executing {side} order for {symbol}...")

        # Simulate execution with slippage
        price = self.context.market_data.get("close", 100)
        slippage = 0.001 # 0.1%
        executed_price = price * (1 + slippage) if side == "BUY" else price * (1 - slippage)

        # Simple PnL simulation: assume we exit at the same tick for simplicity of backtest demo
        # or just track the entry. Here we just simulate a "win" for demo purposes
        # but with more realistic accounting.
        profit_loss = 5.0 # Mocked realized PnL
        self.context.portfolio.total_value += profit_loss

        self.context.memory.add("trade_execution", {
            "symbol": symbol,
            "side": side,
            "entry_price": executed_price,
            "reason": opp.get("reason", "N/A"),
            "pnl": profit_loss
        })
