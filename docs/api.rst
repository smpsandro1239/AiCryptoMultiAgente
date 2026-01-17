REST API Reference
==================

MATF provides a FastAPI-based REST API for remote monitoring and control of the trading system.

Endpoints
---------

* **GET /status**
    Returns the current system status, active agents, and total portfolio value.

* **GET /memory**
    Retrieves the agent decision logs from Semantic Memory.
    Optional query parameter: ``query`` (keyword search).

* **POST /trade/manual**
    Sends a manual trade order to the system.
    Parameters:
        * ``symbol`` (str): e.g., "BTC/USDT"
        * ``side`` (str): "BUY" or "SELL"
        * ``amount`` (float): Order size in USD.

Usage Example
-------------

.. code-block:: python

    import requests
    response = requests.get("http://localhost:8000/status")
    print(response.json())
