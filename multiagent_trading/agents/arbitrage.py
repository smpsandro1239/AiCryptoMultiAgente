from multiagent_trading.agents.base import BaseAgent

class ArbitrageAgent(BaseAgent):
    """
    Identifies price discrepancies for the same asset across different simulated exchanges.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_spread = self.config.get("arbitrage", {}).get("min_spread", 0.001) # 0.1%

    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        self.logger.info(f"{self.name} searching for arbitrage opportunities...")

        # We simulate multiple sources for the same asset
        # Format assumed: Asset:Exchange
        assets = {}
        for key, data in data_batch.items():
            if ":" in key:
                asset, exchange = key.split(":")
                if asset not in assets: assets[asset] = []
                assets[asset].append({"exchange": exchange, "price": data.get("close", 0)})

        for asset, sources in assets.items():
            if len(sources) < 2: continue

            # Find min and max price
            sources.sort(key=lambda x: x["price"])
            min_p = sources[0]
            max_p = sources[-1]

            spread = (max_p["price"] - min_p["price"]) / min_p["price"]

            if spread >= self.min_spread:
                self.logger.info(f"Arbitrage Found! {asset}: {min_p['exchange']}@${min_p['price']} -> {max_p['exchange']}@${max_p['price']} (Spread: {spread:.4%})")

                # Emit arbitrage event
                await self.event_bus.publish("arbitrage_opportunity", {
                    "asset": asset,
                    "buy_exchange": min_p["exchange"],
                    "sell_exchange": max_p["exchange"],
                    "buy_price": min_p["price"],
                    "sell_price": max_p["price"],
                    "spread": spread
                })

                # In a real scenario, this would trigger simultaneous Buy/Sell orders
                # Here we log it in memory
                self.context.memory.add("arbitrage_signal", {
                    "asset": asset,
                    "spread": spread,
                    "exchanges": f"{min_p['exchange']}->{max_p['exchange']}"
                })
