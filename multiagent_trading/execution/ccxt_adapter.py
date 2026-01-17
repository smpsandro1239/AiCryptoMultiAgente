import ccxt
import asyncio

class CCXTAdapter:
    def __init__(self, exchange_id, api_key=None, secret=None, paper_trading=True):
        self.exchange_id = exchange_id
        self.paper_trading = paper_trading
        # In a real scenario, we would initialize the exchange
        # self.exchange = getattr(ccxt, exchange_id)({
        #     'apiKey': api_key,
        #     'secret': secret,
        #     'enableRateLimit': True,
        # })
        self.mock_balance = {"USDT": 10000.0, "BTC": 0.0}

    async def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        """Mock fetching OHLCV data."""
        await asyncio.sleep(0.1) # Simulate network lag
        return [
            [1642320000000, 42000.0, 42500.0, 41800.0, 42300.0, 100.0],
            # ... more candles
        ]

    async def create_order(self, symbol, type, side, amount, price=None):
        """Mock creating an order."""
        await asyncio.sleep(0.2)
        order_id = "mock-order-12345"
        return {
            "id": order_id,
            "symbol": symbol,
            "type": type,
            "side": side,
            "amount": amount,
            "price": price or 42300.0,
            "status": "closed"
        }

    async def fetch_balance(self):
        """Mock fetching balance."""
        return self.mock_balance
