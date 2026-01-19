from multiagent_trading.agents.base import BaseAgent

class StopLossTakeProfitAgent(BaseAgent):
    """
    Agente que monitoriza posições ativas e aciona eventos de saída baseados em stop-loss e take-profit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_loss_pct = self.config.get("stop_loss_pct", 0.02)
        self.take_profit_pct = self.config.get("take_profit_pct", 0.05)

    async def on_market_update(self, data):
        symbol = data.get("symbol")
        current_price = data.get("close")

        # Verificar posições no portfólio (simulado)
        if hasattr(self.context.portfolio, "positions") and symbol in self.context.portfolio.positions:
            position = self.context.portfolio.positions[symbol]
            entry_price = position["entry_price"]
            pnl_pct = (current_price - entry_price) / entry_price

            if pnl_pct <= -self.stop_loss_pct:
                self.logger.info(f"Stop Loss atingido para {symbol}", pnl_pct=pnl_pct)
                await self.event_bus.publish("exit_triggered", {"symbol": symbol, "reason": "STOP_LOSS"})
            elif pnl_pct >= self.take_profit_pct:
                self.logger.info(f"Take Profit atingido para {symbol}", pnl_pct=pnl_pct)
                await self.event_bus.publish("exit_triggered", {"symbol": symbol, "reason": "TAKE_PROFIT"})
