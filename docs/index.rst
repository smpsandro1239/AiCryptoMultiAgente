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
- **RegimeAgent**: Identifies market conditions.
- **ScannerAgent**: Finds trading opportunities.
- **RiskAgent**: Manages position sizing and risk exposure.
- **SupervisorAgent**: Validates trades.
- **ExecutionAgent**: Executes trades on exchanges.

Getting Started
---------------
1. Install dependencies: ``pip install -r requirements.txt``
2. Run backtest: ``python examples/backtest_example.py``
3. Launch dashboard: ``streamlit run multiagent_trading/analytics/dashboard.py``
