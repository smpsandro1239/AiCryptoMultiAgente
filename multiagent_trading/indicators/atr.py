import numpy as np

def atr(high, low, close, period=14):
    """
    Calculate Average True Range.
    """
    if len(close) <= period:
        return np.array([np.nan] * len(close))

    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])

    tr = np.maximum(tr1, np.maximum(tr2, tr3))

    atr_values = np.zeros_like(close, dtype=float)
    atr_values[period] = np.mean(tr[:period])

    for i in range(period + 1, len(close)):
        atr_values[i] = (atr_values[i-1] * (period - 1) + tr[i-1]) / period

    atr_values[:period] = np.nan
    return atr_values
