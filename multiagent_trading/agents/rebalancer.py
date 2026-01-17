from multiagent_trading.agents.base import BaseAgent

class LongShortRebalancingAgent(BaseAgent):
    """
    Maintains target portfolio weights by rebalancing assets.
    Supports Long/Short market neutral strategies.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_weights = self.config.get("rebalance", {}).get("target_weights", {})
        self.rebalance_threshold = self.config.get("rebalance", {}).get("threshold", 0.05)

    async def on_market_update(self, data_batch):
        # Trigger rebalancing check
        if not self.target_weights:
            return

        self.logger.info(f"{self.name} checking portfolio balance...")

        # Calculate current weights
        market_prices = {s: d.get("close", 0) for s, d in self.context.market_data.items()}
        total_value = self.context.portfolio.get_total_value(market_prices)

        if total_value == 0:
            return

        for symbol, target_weight in self.target_weights.items():
            current_qty = self.context.portfolio.positions.get(symbol, 0.0)
            current_price = market_prices.get(symbol, 0)
            if current_price == 0: continue

            current_weight = (current_qty * current_price) / total_value
            weight_diff = target_weight - current_weight

            if abs(weight_diff) > self.rebalance_threshold:
                target_usd = weight_diff * total_value
                side = "BUY" if target_usd > 0 else "SELL"
                self.logger.info(f"{self.name} rebalancing {symbol}: current {current_weight:.2f}, target {target_weight:.2f}")

                # Emit a rebalance order event
                await self.event_bus.publish("trade_approved", {
                    "symbol": symbol,
                    "side": side,
                    "optimized_size": abs(target_usd),
                    "reason": "Portfolio Rebalancing"
                })
