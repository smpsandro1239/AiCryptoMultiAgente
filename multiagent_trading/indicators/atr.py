import numpy as np

def calculate_atr(highs, lows, closes, period=14):
    """Calcula o Average True Range (ATR)."""
    if len(highs) < period + 1:
        return None

    highs = np.array(highs)
    lows = np.array(lows)
    closes = np.array(closes)

    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])

    tr = np.maximum(tr1, np.maximum(tr2, tr3))

    atr = np.zeros_like(closes)
    atr[period] = np.mean(tr[:period])

    for i in range(period + 1, len(closes)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i-1]) / period

    return atr
