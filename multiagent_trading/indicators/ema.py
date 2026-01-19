import numpy as np

import pandas as pd

def calculate_ema(prices, period=14):
    """Calcula a Média Móvel Exponencial (EMA) de forma vetorizada."""
    if len(prices) < period:
        return None

    return pd.Series(prices).ewm(span=period, adjust=False).mean().values
