import pandas as pd

def load_ohlcv_csv(filename):
    """
    Loads OHLCV data from a CSV file.
    Expects columns: timestamp, open, high, low, close, volume
    """
    try:
        df = pd.read_csv(filename)
        return df.to_dict('records')
    except FileNotFoundError:
        # Fallback to mock data for the example if file doesn't exist
        return [
            {"timestamp": 1, "close": 100},
            {"timestamp": 2, "close": 105},
            {"timestamp": 3, "close": 110},
        ]
