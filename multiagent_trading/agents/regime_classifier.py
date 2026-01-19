from multiagent_trading.agents.base import BaseAgent
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd

class RegimeClassifierAgent(BaseAgent):
    """
    Agente que utiliza Machine Learning para classificar o regime de mercado.
    Suporta aprendizagem online através de retreino periódico.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = RandomForestClassifier(n_estimators=100)
        self.data_buffer = []
        self.min_data_points = 50
        self.is_trained = False

    async def on_market_update(self, data):
        features = self._extract_features(data)
        if features is None:
            return

        self.data_buffer.append(features)

        # Manter apenas os últimos 1000 pontos
        if len(self.data_buffer) > 1000:
            self.data_buffer.pop(0)

        if len(self.data_buffer) >= self.min_data_points and not self.is_trained:
            self._train_initial_model()

        if self.is_trained:
            regime = self.model.predict([features])[0]
            self.context.regime = regime
            self.logger.info(f"Regime classificado via ML: {regime}", symbol=data.get("symbol"))
            await self.event_bus.publish("regime_change", regime)

    def _extract_features(self, data):
        # Simulação de extração de features para o classificador
        try:
            return [
                data.get("close", 0),
                data.get("rsi", 50),
                data.get("volatility", 0.02),
                data.get("volume", 1000)
            ]
        except Exception:
            return None

    def _train_initial_model(self):
        self.logger.info("A treinar modelo inicial de classificação de regime...")
        X = np.array(self.data_buffer)
        # Mock de labels para o treino (em produção seriam calculados retroativamente)
        y = ["BULL" if x[0] > np.mean(X[:, 0]) else "BEAR" for x in X]
        self.model.fit(X, y)
        self.is_trained = True
        self.logger.info("Modelo de regime treinado com sucesso.")
