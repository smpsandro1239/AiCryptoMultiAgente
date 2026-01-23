from multiagent_trading.agents.base import BaseAgent
import numpy as np

class StatArbAgent(BaseAgent):
    """
    Agente de Arbitragem Estatística (Pairs Trading).
    Analisa o desvio do spread entre dois ativos cointegrados.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pair = self.config.get("pair", ("BTC/USDT", "ETH/USDT"))
        self.history = {self.pair[0]: [], self.pair[1]: []}
        self.z_threshold = self.config.get("z_threshold", 2.0)

    async def on_market_update(self, data):
        await super().on_market_update(data)

        # Simulação de recolha de preços do par
        # snapshot pode ser multi-símbolo
        if self.pair[0] in data and self.pair[1] in data:
            p1 = data[self.pair[0]]["close"]
            p2 = data[self.pair[1]]["close"]

            self.history[self.pair[0]].append(p1)
            self.history[self.pair[1]].append(p2)

            if len(self.history[self.pair[0]]) > 30:
                self._analyze_pair()

    def _analyze_pair(self):
        y = np.array(self.history[self.pair[0]][-30:])
        x = np.array(self.history[self.pair[1]][-30:])

        # Cálculo de rácio e Z-score do spread
        ratio = y / x
        m = np.mean(ratio)
        s = np.std(ratio)
        z = (ratio[-1] - m) / s if s > 0 else 0

        self.logger.info(f"Análise Stat-Arb {self.pair[0]}/{self.pair[1]}", z_score=z)

        if z > self.z_threshold:
            # Short Y, Long X
            self._generate_signal("SELL", "BUY")
        elif z < -self.z_threshold:
            # Long Y, Short X
            self._generate_signal("BUY", "SELL")

    def _generate_signal(self, side1, side2):
        self.logger.info(f"Oportunidade Stat-Arb detetada!", side1=side1, side2=side2)
        # Em produção, publicaria um sinal para o Supervisor
