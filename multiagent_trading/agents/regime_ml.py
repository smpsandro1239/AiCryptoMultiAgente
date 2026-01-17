import numpy as np
from sklearn.ensemble import RandomForestClassifier
from multiagent_trading.agents.base import BaseAgent

class RegimeClassifierAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = RandomForestClassifier(n_estimators=50)
        self.is_trained = False
        self.features_history = []
        self.labels_history = []
        self.update_interval = self.config.get("regime_ml", {}).get("update_interval", 50)
        self.tick_count = 0

    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        symbol = next(iter(data_batch))
        price = data_batch[symbol].get("close", 100)
        self.tick_count += 1

        if not hasattr(self, 'prices'):
            self.prices = []

        self.prices.append(price)
        if len(self.prices) < 5:
            return

        returns = np.diff(self.prices[-5:]) / self.prices[-5:-1]
        volatility = np.std(returns)
        feature = [returns[-1], volatility]

        # Online Learning / Retraining Logic
        if not self.is_trained:
            self.features_history.append(feature)
            label = "BULL" if returns[-1] > 0.0001 else "BEAR" if returns[-1] < -0.0001 else "SIDEWAYS"
            self.labels_history.append(label)

            if len(self.features_history) >= 20:
                self.train_model()
        else:
            prediction = self.model.predict([feature])[0]
            if prediction != self.context.regime:
                self.logger.info(f"{self.name} Predicted Regime: {prediction}")
                self.context.regime = prediction
                await self.event_bus.publish("regime_change", prediction)

            # Periodic incremental retraining
            self.features_history.append(feature)
            label = "BULL" if returns[-1] > 0.0001 else "BEAR" if returns[-1] < -0.0001 else "SIDEWAYS"
            self.labels_history.append(label)

            if self.tick_count % self.update_interval == 0:
                self.train_model()

    def train_model(self):
        self.logger.info(f"{self.name} Training/Retraining ML Model with {len(self.features_history)} samples...")
        # Use latest samples (sliding window)
        window = 200
        X = self.features_history[-window:]
        y = self.labels_history[-window:]
        self.model.fit(X, y)
        self.is_trained = True
        self.logger.info(f"{self.name} ML Model trained successfully.")
