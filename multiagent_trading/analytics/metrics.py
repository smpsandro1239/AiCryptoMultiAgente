import numpy as np

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """Calcula o Sharpe Ratio anualizado."""
    if len(returns) < 2: return 0.0
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0: return 0.0
    return (avg_return - risk_free_rate) / std_return * np.sqrt(252)

def calculate_max_drawdown(values):
    """Calcula o Maximum Drawdown."""
    if not values: return 0.0
    values = np.array(values)
    peak = np.maximum.accumulate(values)
    drawdown = (values - peak) / peak
    return np.min(drawdown)

def calculate_sortino_ratio(returns, risk_free_rate=0.0):
    """Calcula o Sortino Ratio anualizado."""
    if len(returns) < 2: return 0.0
    avg_return = np.mean(returns)
    downside_returns = [r for r in returns if r < 0]
    if not downside_returns: return 0.0
    std_downside = np.std(downside_returns)
    if std_downside == 0: return 0.0
    return (avg_return - risk_free_rate) / std_downside * np.sqrt(252)
