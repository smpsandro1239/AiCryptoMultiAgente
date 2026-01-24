from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    """
    Detecta anomalias em séries temporais (preços ou PnL) utilizando Isolation Forest.
    """
    def __init__(self, contamination=0.01):
        self.model = IsolationForest(contamination=contamination)
        self.history = []

    def fit_predict(self, data_point: float):
        self.history.append([data_point])
        if len(self.history) < 20: # Mínimo de dados para começar
            return 1 # Normal por defeito enquanto treina

        # Re-treino rápido (simplificado)
        X = np.array(self.history[-500:]) # Analisar os últimos 500 pontos
        self.model.fit(X)

        prediction = self.model.predict([[data_point]])[0]
        return prediction # 1 para normal, -1 para anomalia

    def is_anomaly(self, data_point: float) -> bool:
        return self.fit_predict(data_point) == -1
