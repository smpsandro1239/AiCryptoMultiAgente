import numpy as np

import pandas as pd

def calculate_rsi(prices, period=14):
    """Calcula o Índice de Força Relativa (RSI) de forma vetorizada."""
    if len(prices) < period + 1:
        return None

    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.values
