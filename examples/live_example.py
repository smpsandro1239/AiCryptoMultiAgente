import asyncio
from multiagent_trading.core.orchestrator import EventBus, Context, Orchestrator
from multiagent_trading.core.logger import Logger
from multiagent_trading.execution.ccxt_adapter import CCXTAdapter
from multiagent_trading.agents import ScannerAgent, ExecutionAgent

async def main():
    logger = Logger()
    event_bus = EventBus()
    context = Context()

    # Simulação de adaptador live (paper trading ativo por defeito)
    adapter = CCXTAdapter('binance')

    agents = [
        ScannerAgent("Scanner", {}, context, event_bus, logger),
        ExecutionAgent("Execution", {}, context, event_bus, logger)
    ]

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    logger.info("A iniciar simulação live para BTC/USDT...")

    # Em um cenário real, usaríamos adapter.watch_ohlcv
    # Aqui simulamos um único tick para o exemplo
    market_snapshot = {"symbol": "BTC/USDT", "close": 50000, "timestamp": "2026-01-19T11:00:00"}
    await orchestrator.step(market_snapshot)

    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
