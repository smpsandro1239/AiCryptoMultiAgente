import asyncio
import time
from multiagent_trading.core.orchestrator import EventBus, Context, Orchestrator
from multiagent_trading.core.logger import Logger
from multiagent_trading.agents import BaseAgent

async def run_stress_test(num_agents=1000):
    eb = EventBus()
    logger = Logger(level="WARNING")
    ctx = Context()

    print(f"🚀 A iniciar teste de stress com {num_agents} agentes...")

    agents = []
    for i in range(num_agents):
        # Usar BaseAgent para minimizar overhead
        agents.append(BaseAgent(f"Agent_{i}", {}, ctx, eb, logger))

    orchestrator = Orchestrator(agents, ctx, eb, logger)

    start_time = time.time()

    # Disparar um evento que todos os agentes ouvem
    snapshot = {"timestamp": time.time(), "close": 100}
    await orchestrator.step(snapshot)

    end_time = time.time()
    total_latency = (end_time - start_time) * 1000

    print(f"✅ Concluído! Tempo de resposta para {num_agents} agentes: {total_latency:.2f}ms")
    print(f"📊 Latência média por agente: {total_latency/num_agents:.4f}ms")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
