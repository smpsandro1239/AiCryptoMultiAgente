from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")
PRICE_COLUMNS = ("open", "high", "low", "close")


def _synthetic_ohlcv() -> list[dict]:
    """Return a tiny, explicitly requested dataset for demonstrations only."""
    return [
        {"timestamp": 1, "open": 99, "high": 101, "low": 98, "close": 100, "volume": 10},
        {"timestamp": 2, "open": 100, "high": 106, "low": 99, "close": 105, "volume": 12},
        {"timestamp": 3, "open": 105, "high": 111, "low": 104, "close": 110, "volume": 15},
    ]


def load_ohlcv_csv(filename: str | Path, *, allow_synthetic: bool = False) -> list[dict]:
    """Load and validate OHLCV candles; synthetic data is opt-in only."""
    path = Path(filename)
    if not path.is_file():
        if allow_synthetic:
            return _synthetic_ohlcv()
        raise FileNotFoundError(f"OHLCV CSV not found: {path}")

    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"OHLCV CSV is missing required columns: {", ".join(missing)}")
    if frame.empty:
        raise ValueError("OHLCV CSV contains no candles")
    if frame["timestamp"].isna().any():
        raise ValueError("OHLCV timestamps cannot be empty")
    if frame["timestamp"].duplicated().any():
        raise ValueError("OHLCV timestamps must be unique")

    for column in (*PRICE_COLUMNS, "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if frame[column].isna().any():
            raise ValueError(f"OHLCV column {column!r} contains empty values")

    values = frame[[*PRICE_COLUMNS, "volume"]].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("OHLCV values must be finite numbers")
    if (frame[list(PRICE_COLUMNS)] <= 0).any().any():
        raise ValueError("OHLC prices must be greater than zero")
    if (frame["volume"] < 0).any():
        raise ValueError("OHLCV volume cannot be negative")
    if (frame["high"] < frame["low"]).any():
        raise ValueError("OHLCV high cannot be lower than low")
    if (frame["high"] < frame[["open", "close"]].max(axis=1)).any():
        raise ValueError("OHLCV high must be greater than or equal to open and close")
    if (frame["low"] > frame[["open", "close"]].min(axis=1)).any():
        raise ValueError("OHLCV low must be lower than or equal to open and close")

    return frame.to_dict("records")