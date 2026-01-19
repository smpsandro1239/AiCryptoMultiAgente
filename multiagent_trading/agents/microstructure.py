from multiagent_trading.agents.base import BaseAgent
from multiagent_trading.models.market_depth import MarketDepth

class MicrostructureAgent(BaseAgent):
    """
    Agente que analisa spreads de compra e venda e profundidade/desequilíbrio do order book.
    """
    async def on_market_update(self, data):
        depth_data = data.get("depth")
        if not depth_data:
            return

        depth = MarketDepth(
            symbol=data.get("symbol"),
            bids=depth_data.get("bids", []),
            asks=depth_data.get("asks", [])
        )

        spread = depth.get_spread()
        imbalance = depth.get_imbalance()

        self.logger.info(
            f"Análise de Microestrutura para {depth.symbol}",
            spread=spread,
            imbalance=imbalance
        )

        # Publicar eventos baseados em desequilíbrio significativo
        if abs(imbalance) > 0.5:
            await self.event_bus.publish("microstructure_signal", {
                "symbol": depth.symbol,
                "imbalance": imbalance,
                "side": "BUY" if imbalance > 0 else "SELL"
            })
