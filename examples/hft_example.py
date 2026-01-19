import asyncio
from multiagent_trading.core.orchestrator import EventBus, Context, Orchestrator
from multiagent_trading.core.logger import Logger
from multiagent_trading.agents import (
    ScalpingAgent, MVOOptimizerAgent, RiskAgent, SupervisorAgent, ExecutionAgent, LLMAgent
)
from multiagent_trading.models.portfolio import PortfolioState

async def main():
    logger = Logger()
    event_bus = EventBus()
    portfolio = PortfolioState(initial_value=5000)
    context = Context(portfolio=portfolio)

    # Configuração para HFT
    agents = [
        ScalpingAgent("Scalper", {}, context, event_bus, logger),
        MVOOptimizerAgent("Optimizer", {"risk_aversion": 2.0}, context, event_bus, logger),
        RiskAgent("Risk", {}, context, event_bus, logger),
        LLMAgent("LLM", {}, context, event_bus, logger), # Raciocínio qualitativo rápido
        SupervisorAgent("Supervisor", {}, context, event_bus, logger),
        ExecutionAgent("Execution", {}, context, event_bus, logger)
    ]

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    logger.info("A iniciar simulação HFT/Scalping...")

    # Simulação de rajada de ticks
    for i in range(15):
        price = 50000 + i * 100 # Momentum ascendente significativo
        market_snapshot = {"symbol": "BTC/USDT", "close": price, "timestamp": f"2026-01-19T12:00:{i:02d}"}
        await orchestrator.step(market_snapshot)
        await asyncio.sleep(0.1) # Simulação de HFT

    logger.info(f"Simulação concluída. Valor final: {context.portfolio.total_value}")

if __name__ == "__main__":
    asyncio.run(main())
