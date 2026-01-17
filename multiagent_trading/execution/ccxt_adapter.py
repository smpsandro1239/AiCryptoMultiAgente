import ccxt
import asyncio
import pandas as pd

class CCXTAdapter:
    def __init__(self, exchange_id='binance', paper_trading=True):
        self.exchange_id = exchange_id
        self.paper_trading = paper_trading
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
        })
        self.mock_balance = {"USDT": 10000.0}

    async def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        """Fetch real OHLCV data from the exchange (public endpoint)."""
        try:
            # Note: loop.run_in_executor might be needed if ccxt isn't using async internally here,
            # but modern ccxt has async support. For this adapter we use standard ccxt.
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"Error fetching real OHLCV: {e}")
            # Fallback to mock
            return [[1642320000000, 42000.0, 42500.0, 41800.0, 42300.0, 100.0]]

    async def create_order(self, symbol, type, side, amount, price=None):
        """Mock creating an order (safety first)."""
        await asyncio.sleep(0.1)
        return {
            "id": f"mock-{side}-{symbol}",
            "status": "closed",
            "price": price or 42000.0,
            "amount": amount
        }

    async def fetch_balance(self):
        """Mock fetching balance."""
        return self.mock_balance

    def close(self):
        # self.exchange.close()
        pass
