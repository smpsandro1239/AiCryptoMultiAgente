import numpy as np

def rsi(data, period=14):
    """
    Calculate Relative Strength Index.
    """
    if len(data) <= period:
        return np.array([np.nan] * len(data))

    delta = np.diff(data)
    gain = (delta > 0) * delta
    loss = (delta < 0) * -delta

    avg_gain = np.zeros_like(data, dtype=float)
    avg_loss = np.zeros_like(data, dtype=float)

    avg_gain[period] = np.mean(gain[:period])
    avg_loss[period] = np.mean(loss[:period])

    for i in range(period + 1, len(data)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gain[i-1]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + loss[i-1]) / period

    rs = avg_gain / (avg_loss + 1e-10)
    rsi_values = 100 - (100 / (1 + rs))

    rsi_values[:period] = np.nan
    return rsi_values
