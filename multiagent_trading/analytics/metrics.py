import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculate the Sharpe Ratio.
    """
    if len(returns) < 2:
        return 0.0
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return 0.0
    return (mean_return - risk_free_rate) / std_return * np.sqrt(365 * 24) # Annualized (hourly data)

def calculate_sortino_ratio(returns, risk_free_rate=0.0, target_return=0.0):
    """
    Calculate the Sortino Ratio.
    """
    if len(returns) < 2:
        return 0.0
    mean_return = np.mean(returns)
    downside_returns = [r for r in returns if r < target_return]
    if not downside_returns:
        return 0.0
    downside_std = np.std(downside_returns)
    if downside_std == 0:
        return 0.0
    return (mean_return - risk_free_rate) / downside_std * np.sqrt(365 * 24)

def calculate_max_drawdown(values):
    """
    Calculate the Maximum Drawdown.
    """
    if not values:
        return 0.0
    peak = values[0]
    max_dd = 0
    for v in values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd

def get_performance_metrics(pnl_history):
    """
    Return a dictionary of performance metrics from PnL history.
    """
    if not pnl_history:
        return {}

    values = [p["value"] for p in pnl_history]
    returns = pd.Series(values).pct_change().dropna().tolist()

    return {
        "total_return": (values[-1] / values[0] - 1) if len(values) > 0 else 0,
        "sharpe_ratio": calculate_sharpe_ratio(returns),
        "sortino_ratio": calculate_sortino_ratio(returns),
        "max_drawdown": calculate_max_drawdown(values)
    }
