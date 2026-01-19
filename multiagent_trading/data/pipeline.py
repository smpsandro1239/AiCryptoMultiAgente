import pandas as pd
import numpy as np

class DataPipeline:
    """
    Pipeline de dados para normalização, limpeza e preparação de dados de mercado.
    """
    @staticmethod
    def normalize(df: pd.DataFrame, columns: list):
        """Normaliza as colunas especificadas para o intervalo [0, 1]."""
        result = df.copy()
        for col in columns:
            max_val = df[col].max()
            min_val = df[col].min()
            result[col] = (df[col] - min_val) / (max_val - min_val)
        return result

    @staticmethod
    def clean_outliers(df: pd.DataFrame, col: str, z_threshold: float = 3.0):
        """Remove outliers baseados no Z-score."""
        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
        return df[z_scores < z_threshold]

    @staticmethod
    def prepare_features(df: pd.DataFrame):
        """Adiciona features básicas para modelos de ML."""
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['volatility'] = df['returns'].rolling(window=20).std()
        return df.dropna()
