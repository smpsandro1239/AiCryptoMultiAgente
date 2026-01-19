import numpy as np

def calculate_bollinger_bands(prices, period=20, num_std=2):
    """Calcula as Bandas de Bollinger."""
    if len(prices) < period:
        return None, None, None

    prices = np.array(prices)
    sma = np.zeros_like(prices)
    upper_band = np.zeros_like(prices)
    lower_band = np.zeros_like(prices)

    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1 : i + 1]
        mean = np.mean(window)
        std = np.std(window)
        sma[i] = mean
        upper_band[i] = mean + (num_std * std)
        lower_band[i] = mean - (num_std * std)

    return upper_band, sma, lower_band
