from typing import List, Dict

class MarketDepth:
    """
    Modelo que representa o estado do order book com níveis de preço e quantidade.
    """
    def __init__(self, symbol: str, bids: List[Dict[str, float]], asks: List[Dict[str, float]]):
        self.symbol = symbol
        self.bids = bids # [{"price": 100, "amount": 1.0}, ...]
        self.asks = asks

    def get_mid_price(self):
        if not self.bids or not self.asks:
            return None
        return (self.bids[0]["price"] + self.asks[0]["price"]) / 2.0

    def get_spread(self):
        if not self.bids or not self.asks:
            return None
        return self.asks[0]["price"] - self.bids[0]["price"]

    def get_imbalance(self):
        bid_vol = sum(b["amount"] for b in self.bids)
        ask_vol = sum(a["amount"] for a in self.asks)
        return (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0
