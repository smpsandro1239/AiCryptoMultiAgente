from typing import List, Tuple

class MarketDepth:
    """
    Represents the order book depth for a symbol.
    """
    def __init__(self, symbol: str, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]):
        self.symbol = symbol
        self.bids = bids # List of (price, quantity)
        self.asks = asks # List of (price, quantity)

    def get_best_bid(self) -> float:
        return self.bids[0][0] if self.bids else 0.0

    def get_best_ask(self) -> float:
        return self.asks[0][0] if self.asks else 0.0

    def get_spread(self) -> float:
        return self.get_best_ask() - self.get_best_bid()

    def get_imbalance(self) -> float:
        bid_vol = sum(q for p, q in self.bids)
        ask_vol = sum(q for p, q in self.asks)
        if bid_vol + ask_vol == 0:
            return 0.0
        return (bid_vol - ask_vol) / (bid_vol + ask_vol)
