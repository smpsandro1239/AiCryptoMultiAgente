import numpy as np

def macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate Moving Average Convergence Divergence.
    """
    from multiagent_trading.indicators.ema import ema

    fast_ema = ema(data, fast_period)
    slow_ema = ema(data, slow_period)

    macd_line = fast_ema - slow_ema

    # Calculate signal line using EMA of MACD line
    # We need to filter out NaNs for the EMA calculation
    valid_mask = ~np.isnan(macd_line)
    valid_macd = macd_line[valid_mask]

    signal_line = np.full_like(macd_line, np.nan)
    if len(valid_macd) >= signal_period:
        signal_line[valid_mask] = ema(valid_macd, signal_period)

    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram
