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

    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        symbol = next(iter(data_batch))
        price = data_batch[symbol].get("close", 100)

        # Simple feature engineering: Returns and Volatility
        if not hasattr(self, 'prices'):
            self.prices = []

        self.prices.append(price)
        if len(self.prices) < 5:
            return

        returns = np.diff(self.prices[-5:]) / self.prices[-5:-1]
        volatility = np.std(returns)
        feature = [returns[-1], volatility]

        if not self.is_trained:
            # Collect data for training
            self.features_history.append(feature)
            # Pseudo-labeling for the sake of the example
            label = "BULL" if returns[-1] > 0 else "BEAR"
            self.labels_history.append(label)

            if len(self.features_history) > 20:
                self.model.fit(self.features_history, self.labels_history)
                self.is_trained = True
                self.logger.info(f"{self.name} ML Model trained.")
        else:
            prediction = self.model.predict([feature])[0]
            if prediction != self.context.regime:
                self.logger.info(f"{self.name} Predicted Regime: {prediction}")
                self.context.regime = prediction
                await self.event_bus.publish("regime_change", prediction)
