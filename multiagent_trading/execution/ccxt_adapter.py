import ccxt
import asyncio
import time

class CCXTAdapter:
    """
    Adaptador para a biblioteca CCXT, suportando paper trading e dados reais.
    """
    def __init__(self, exchange_id, api_key=None, secret=None, paper_trading=True):
        self.exchange_class = getattr(ccxt, exchange_id)
        self.exchange = self.exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        if paper_trading:
            self.exchange.set_sandbox_mode(True)

    async def fetch_ohlcv(self, symbol, timeframe='1m', limit=100):
        return await asyncio.to_thread(self.exchange.fetch_ohlcv, symbol, timeframe, limit=limit)

    async def create_order(self, symbol, type, side, amount, price=None):
        return await asyncio.to_thread(self.exchange.create_order, symbol, type, side, amount, price)

    async def watch_ohlcv(self, symbol, timeframe='1m'):
        """Simulação de watch_ohlcv (em um cenário real usaria websockets do ccxt.pro)"""
        while True:
            data = await self.fetch_ohlcv(symbol, timeframe, limit=1)
            if data:
                yield data[0]
            await asyncio.sleep(60)

    async def watch_trades(self, symbol):
        """Simulação de watch_trades via WebSockets."""
        while True:
            # Mock de trade em tempo real
            trade = {
                'symbol': symbol,
                'price': 50000 + (asyncio.get_event_loop().time() % 100),
                'amount': 0.01,
                'timestamp': int(time.time() * 1000)
            }
            yield trade
            await asyncio.sleep(1) # Simula trades a cada segundo
