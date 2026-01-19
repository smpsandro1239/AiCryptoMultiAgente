import numpy as np

def calculate_ema(prices, period=14):
    """Calcula a Média Móvel Exponencial (EMA)."""
    if len(prices) < period:
        return None

    prices = np.array(prices)
    alpha = 2 / (period + 1)
    ema = np.zeros_like(prices)
    ema[period-1] = np.mean(prices[:period])

    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * alpha + ema[i-1]

    return ema
