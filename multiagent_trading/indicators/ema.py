import numpy as np

def ema(data, period):
    """
    Calculate Exponential Moving Average.
    """
    if len(data) < period:
        return np.array([np.nan] * len(data))

    values = np.array(data)
    alpha = 2 / (period + 1)
    ema_values = np.zeros_like(values, dtype=float)
    ema_values[period-1] = np.mean(values[:period])

    for i in range(period, len(values)):
        ema_values[i] = (values[i] - ema_values[i-1]) * alpha + ema_values[i-1]

    ema_values[:period-1] = np.nan
    return ema_values
