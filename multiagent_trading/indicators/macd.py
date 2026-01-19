from multiagent_trading.indicators.ema import calculate_ema

def calculate_macd(prices, slow=26, fast=12, signal=9):
    """Calcula o MACD (Moving Average Convergence Divergence)."""
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)

    if ema_fast is None or ema_slow is None:
        return None, None, None

    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line[slow-1:], signal)

    # Pad signal_line to match macd_line length
    import numpy as np
    full_signal_line = np.zeros_like(macd_line)
    full_signal_line[:] = np.nan
    if signal_line is not None:
        full_signal_line[slow-1+signal-1:] = signal_line[signal-1:]

    histogram = macd_line - full_signal_line

    return macd_line, full_signal_line, histogram
