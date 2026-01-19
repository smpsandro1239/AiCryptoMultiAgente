from multiagent_trading.agents.base import BaseAgent
import numpy as np

class RiskParityOptimizerAgent(BaseAgent):
    """
    Agente que implementa alocação de capital baseada no inverso da volatilidade do ativo.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("risk_assessed", self.on_risk_assessed)

    async def on_risk_assessed(self, opp):
        self.logger.info(f"{self.name} a otimizar alocação via Risk Parity para {opp['symbol']}...")

        # Simulação de cálculo de volatilidade (em um cenário real viria dos indicadores/dados históricos)
        volatility = opp.get("volatility", 0.02)

        # Alocação inversamente proporcional à volatilidade
        allocation = 1.0 / volatility
        opp["allocation"] = allocation

        await self.event_bus.publish("allocation_optimized", opp)
