import asyncio
from multiagent_trading.core.orchestrator import EventBus, Context, Orchestrator
from multiagent_trading.core.logger import Logger
from multiagent_trading.agents import (
    RegimeAgent, ScannerAgent, RiskAgent, SupervisorAgent,
    ExecutionAgent, LLMAgent, SentimentAgent, MicrostructureAgent
)
from multiagent_trading.models.portfolio import PortfolioState

async def main():
    logger = Logger()
    event_bus = EventBus()
    portfolio = PortfolioState(initial_value=10000)
    context = Context(portfolio=portfolio)

    agents = [
        RegimeAgent("Regime", {}, context, event_bus, logger),
        ScannerAgent("Scanner", {}, context, event_bus, logger),
        RiskAgent("Risk", {}, context, event_bus, logger),
        LLMAgent("LLM", {}, context, event_bus, logger),
        SupervisorAgent("Supervisor", {}, context, event_bus, logger),
        ExecutionAgent("Execution", {}, context, event_bus, logger),
        SentimentAgent("Sentiment", {}, context, event_bus, logger),
        MicrostructureAgent("Microstructure", {}, context, event_bus, logger)
    ]

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    # Simulação de market data multi-símbolo
    market_snapshot = {
        "BTC/USDT": {"close": 50000, "rsi": 60, "timestamp": "2026-01-19T10:00:00"},
        "ETH/USDT": {"close": 3000, "rsi": 40, "timestamp": "2026-01-19T10:00:00"}
    }

    logger.info("A iniciar simulação de estratégia complexa...")
    await orchestrator.step(market_snapshot)

    # Aguardar processamento asíncrono
    await asyncio.sleep(2)
    logger.info(f"Valor final do portfólio: {context.portfolio.total_value}")

if __name__ == "__main__":
    asyncio.run(main())
