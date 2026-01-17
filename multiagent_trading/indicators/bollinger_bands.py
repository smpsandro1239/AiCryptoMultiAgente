import numpy as np

def bollinger_bands(data, period=20, std_dev=2):
    """
    Calculate Bollinger Bands.
    """
    if len(data) < period:
        nan_arr = np.full(len(data), np.nan)
        return nan_arr, nan_arr, nan_arr

    values = np.array(data)
    middle_band = np.full_like(values, np.nan, dtype=float)
    upper_band = np.full_like(values, np.nan, dtype=float)
    lower_band = np.full_like(values, np.nan, dtype=float)

    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        ma = np.mean(window)
        sd = np.std(window)

        middle_band[i] = ma
        upper_band[i] = ma + (std_dev * sd)
        lower_band[i] = ma - (std_dev * sd)

    return upper_band, middle_band, lower_band
