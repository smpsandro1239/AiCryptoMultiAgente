import asyncio
from multiagent_trading.core.orchestrator import EventBus, Context, Orchestrator
from multiagent_trading.core.logger import Logger
from multiagent_trading.agents import (
    RegimeClassifierAgent, ScannerAgent, RiskAgent, SupervisorAgent, ExecutionAgent, LLMAgent
)
from multiagent_trading.models.portfolio import PortfolioState

async def main():
    logger = Logger()
    event_bus = EventBus()
    portfolio = PortfolioState()
    context = Context(portfolio=portfolio)

    # Agentes com Classificador de Regime ML
    agents = [
        RegimeClassifierAgent("MLRegime", {}, context, event_bus, logger),
        ScannerAgent("Scanner", {}, context, event_bus, logger),
        RiskAgent("Risk", {}, context, event_bus, logger),
        LLMAgent("LLM", {}, context, event_bus, logger),
        SupervisorAgent("Supervisor", {}, context, event_bus, logger),
        ExecutionAgent("Execution", {}, context, event_bus, logger)
    ]

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    logger.info("A iniciar exemplo de ML Regime Classification...")

    # Gerar 60 ticks para treinar o classificador (min_data_points=50)
    for i in range(60):
        price = 100 + (i % 10) # Ciclo de preços
        market_snapshot = {"symbol": "BTC/USDT", "close": price, "rsi": 50 + i, "timestamp": f"T{i}"}
        await orchestrator.step(market_snapshot)

    await asyncio.sleep(1)
    logger.info(f"Estado final do regime: {context.regime}")
    logger.info(f"Valor do portfólio: {portfolio.total_value}")

if __name__ == "__main__":
    asyncio.run(main())
