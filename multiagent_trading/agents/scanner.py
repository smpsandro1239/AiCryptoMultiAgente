"""Demonstration scanner that forwards only fields supplied by market data."""
from multiagent_trading.agents.base import BaseAgent


class ScannerAgent(BaseAgent):
    """Convert a market snapshot into an intent without fabricating prices."""

    async def on_market_update(self, data):
        self.logger.info(
            f"{self.name} a procurar oportunidades...",
            symbol=data.get("symbol"),
        )
        opportunity = {
            "symbol": data.get("symbol", ""),
            "side": data.get("side", "BUY"),
            "entry_price": data.get("entry_price", data.get("close")),
            "stop_price": data.get("stop_price"),
        }
        await self.event_bus.publish("opportunity_found", opportunity)
