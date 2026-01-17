from multiagent_trading.agents.base import BaseAgent

class MicrostructureAgent(BaseAgent):
    """
    Analyzes market microstructure: order book depth, bid-ask spread, and liquidity.
    """
    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        self.logger.info(f"{self.name} analyzing market microstructure...")

        for symbol, data in data_batch.items():
            # Mock order book analysis
            # In a real scenario, 'data' would contain 'order_book'
            bid = data.get("close", 100) * 0.9999
            ask = data.get("close", 100) * 1.0001
            spread = (ask - bid) / ask

            # Simulated depth
            bid_depth = 50.0 # units
            ask_depth = 45.0 # units
            imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth)

            self.logger.info(f"Microstructure for {symbol}: Spread={spread:.6f}, Imbalance={imbalance:.2f}")

            # Store in context for other agents (e.g. ExecutionAgent) to use
            if not hasattr(self.context, 'microstructure'):
                self.context.microstructure = {}

            self.context.microstructure[symbol] = {
                "spread": spread,
                "imbalance": imbalance,
                "liquidity_ok": spread < 0.001 # Policy check
            }

            await self.event_bus.publish("microstructure_update", self.context.microstructure[symbol])
