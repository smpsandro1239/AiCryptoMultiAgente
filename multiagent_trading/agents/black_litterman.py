from multiagent_trading.agents.base import BaseAgent
import numpy as np

class BlackLittermanAgent(BaseAgent):
    """
    Agente que implementa o modelo Black-Litterman para otimização de portfólio.
    Combina o equilíbrio de mercado com visões específicas dos agentes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tau = 0.05 # Escala de incerteza da prior
        self.event_bus.subscribe("opportunity_found", self.on_opportunity)

    async def on_opportunity(self, opp):
        self.logger.info(f"{self.name} a aplicar modelo Black-Litterman para {opp['symbol']}...")

        # Simulação de parâmetros do modelo
        # Pi: Retornos implícitos de equilíbrio
        # Q: Visões dos agentes
        # P: Matriz de ligação das visões aos ativos
        # Sigma: Matriz de covariância

        # Simplificação para demonstração
        pi = np.array([0.03, 0.02])
        q = np.array([0.05]) # Visão otimista de 5% de retorno
        p = np.array([[1, 0]]) # A visão aplica-se apenas ao primeiro ativo
        sigma = np.array([[0.0004, 0.0001], [0.0001, 0.0003]])
        omega = np.array([[0.00001]]) # Incerteza da visão

        # Fórmula de Black-Litterman para retornos combinados (Er)
        term1 = np.linalg.inv(np.linalg.inv(self.tau * sigma) + np.dot(p.T, np.dot(np.linalg.inv(omega), p)))
        term2 = np.dot(np.linalg.inv(self.tau * sigma), pi) + np.dot(p.T, np.dot(np.linalg.inv(omega), q))
        er = np.dot(term1, term2)

        self.logger.info(f"Retornos ajustados Black-Litterman calculados", expected_return=float(er[0]))
        opp["bl_expected_return"] = float(er[0])
        await self.event_bus.publish("allocation_optimized", opp)
