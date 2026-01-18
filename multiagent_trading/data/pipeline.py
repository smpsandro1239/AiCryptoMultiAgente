import pandas as pd
import numpy as np

class DataPipeline:
    """
    Handles data normalization, cleaning, and feature engineering for the multi-agent system.
    """
    def __init__(self):
        pass

    def process_batch(self, data_batch: dict):
        """
        Normalizes and cleans a batch of market data.
        """
        cleaned_batch = {}
        for symbol, data in data_batch.items():
            # Example cleaning: Ensure price is non-negative
            price = max(0, data.get("close", 0))

            # Example normalization: Log returns (if history available in a real pipeline)

            cleaned_batch[symbol] = {
                "close": price,
                "timestamp": data.get("timestamp"),
                "high": data.get("high", price),
                "low": data.get("low", price),
                "volume": data.get("volume", 0)
            }
        return cleaned_batch

    def handle_outliers(self, series: pd.Series):
        """
        Removes outliers from a data series.
        """
        mean = series.mean()
        std = series.std()
        return series.clip(lower=mean - 3*std, upper=mean + 3*std)
