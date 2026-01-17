MATF: Multi-Agent Trading Framework
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   architecture
   agents
   indicators
   examples

Introduction
------------
The Multi-Agent Trading Framework (MATF) is a modular, AI-native system designed for cryptocurrency markets.

Architecture
------------
MATF uses an event-driven architecture powered by an asynchronous event bus. Agents communicate via events, ensuring loose coupling and high scalability.

Agents
------
- **RegimeAgent**: Identifies market conditions (Bull, Bear, Sideways) using MACD and RSI.
- **ScannerAgent**: Finds trading opportunities across multiple symbols using technical indicators.
- **RiskAgent**: Manages position sizing and risk exposure per trade.
- **PortfolioOptimizerAgent**: Optimizes capital allocation across the entire portfolio.
- **SupervisorAgent**: Validates trades and provides final approval.
- **ExecutionAgent**: Executes trades using Market or TWAP strategies via CCXT.

Indicators
----------
- **EMA**: Exponential Moving Average.
- **RSI**: Relative Strength Index.
- **ATR**: Average True Range.
- **MACD**: Moving Average Convergence Divergence.
- **Bollinger Bands**: Volatility bands based on standard deviation.

Getting Started
---------------
1. Install dependencies: ``pip install -r requirements.txt``
2. Run backtest: ``python examples/backtest_example.py``
3. Launch dashboard: ``streamlit run multiagent_trading/analytics/dashboard.py``
