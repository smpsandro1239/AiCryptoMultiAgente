from multiagent_trading.agents.base import BaseAgent

class StopLossTakeProfitAgent(BaseAgent):
    """
    Monitors open positions and triggers exit events based on Stop Loss and Take Profit levels.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sl_pct = self.config.get("risk", {}).get("stop_loss", 0.02) # 2% SL
        self.tp_pct = self.config.get("risk", {}).get("take_profit", 0.05) # 5% TP
        self.active_trades = {} # symbol: {entry_price, side, qty}

    async def on_market_update(self, data_batch):
        # Update active trades with latest execution info from memory
        executions = self.context.memory.get_by_key("execution")
        for ex in executions:
            val = ex["value"]
            symbol = val["symbol"]
            if symbol not in self.active_trades:
                # Simple logic: assume one active trade per symbol for this agent
                self.active_trades[symbol] = {
                    "entry_price": val.get("price", 0),
                    "side": val["side"],
                    "qty": val.get("qty", 0)
                }

        # Monitor prices
        for symbol, data in data_batch.items():
            if symbol in self.active_trades:
                trade = self.active_trades[symbol]
                current_price = data.get("close", 0)
                entry_price = trade["entry_price"]
                side = trade["side"]

                if entry_price == 0: continue

                pnl_pct = (current_price - entry_price) / entry_price if side == "BUY" else (entry_price - current_price) / entry_price

                exit_triggered = False
                reason = ""

                if pnl_pct <= -self.sl_pct:
                    exit_triggered = True
                    reason = f"Stop Loss Triggered ({pnl_pct:.2%})"
                elif pnl_pct >= self.tp_pct:
                    exit_triggered = True
                    reason = f"Take Profit Triggered ({pnl_pct:.2%})"

                if exit_triggered:
                    self.logger.info(f"{self.name} triggering EXIT for {symbol}: {reason}")
                    exit_side = "SELL" if side == "BUY" else "BUY"

                    await self.event_bus.publish("trade_approved", {
                        "symbol": symbol,
                        "side": exit_side,
                        "optimized_size": trade["qty"] * current_price,
                        "reason": reason
                    })

                    # Remove from active trades after triggering exit
                    del self.active_trades[symbol]
