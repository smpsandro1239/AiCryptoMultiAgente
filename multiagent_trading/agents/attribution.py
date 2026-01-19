from multiagent_trading.agents.base import BaseAgent
import json

class PerformanceAttributionAgent(BaseAgent):
    """
    Agente que analisa os resultados das trocas e atribui o PnL a fatores específicos.
    (Estratégia, Regime, Sentimento, etc.)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade)

    async def on_trade(self, opp):
        # Atribuição simples baseada nos dados da oportunidade
        attribution = {
            "symbol": opp.get("symbol"),
            "strategy": opp.get("strategy", "DEFAULT"),
            "regime": self.context.regime,
            "rationale": opp.get("rationale")
        }

        self.logger.info(f"Atribuição de Performance registada para {opp['symbol']}", strategy=attribution["strategy"])
        self.context.memory.add("performance_attribution", attribution)
