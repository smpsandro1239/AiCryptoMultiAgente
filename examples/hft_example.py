import asyncio
import sys
import os

# Adicionar raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multiagent_trading.core.orchestrator import Orchestrator, EventBus, Logger, Context, SemanticMemory, Backtester
from multiagent_trading.agents.scalping import ScalpingAgent
from multiagent_trading.agents.mvo_optimizer import MVOOptimizerAgent
from multiagent_trading.agents.risk import RiskAgent
from multiagent_trading.agents.supervisor import SupervisorAgent
from multiagent_trading.agents.execution import ExecutionAgent
from multiagent_trading.models.portfolio import PortfolioState

async def run_hft_simulation():
    print("A iniciar Simulação HFT / Scalping...")

    config = {
        "scalping": {"window": 3, "threshold": 0.0002},
        "mvo": {"risk_aversion": 2.0}
    }

    event_bus = EventBus()
    logger = Logger()

    context = Context(
        portfolio=PortfolioState(initial_value=50000),
        config=config
    )

    agents = {
        "scalper": ScalpingAgent("scalper_hft", config, context, event_bus, logger),
        "optimizer": MVOOptimizerAgent("markowitz_mvo", config, context, event_bus, logger),
        "risk": RiskAgent("risk_manager", config, context, event_bus, logger),
        "supervisor": SupervisorAgent("supervisor", config, context, event_bus, logger),
        "execution": ExecutionAgent("fast_execution", config, context, event_bus, logger),
    }

    orchestrator = Orchestrator(agents, context, event_bus, logger)

    # Feed de dados de alta frequência (simulado)
    data_feed = []
    base_btc = 45000
    base_eth = 2400

    for i in range(100):
        # Pequenas variações para testar o scalper
        btc_p = base_btc + (np.random.randn() * 5)
        eth_p = base_eth + (np.random.randn() * 2)
        data_feed.append({
            "BTC/USDT": {"timestamp": i, "close": btc_p},
            "ETH/USDT": {"timestamp": i, "close": eth_p}
        })

    bt = Backtester(orchestrator, data_feed, context)
    results = await bt.run(save_path="hft_backtest_results.json")

    print(f"\nSimulação HFT Concluída.")
    print(f"Valor Final do Portfólio: ${context.portfolio.total_value:,.2f}")

if __name__ == "__main__":
    import numpy as np
    asyncio.run(run_hft_simulation())
