Guia Rápido: Começar com o MATF
=================================

Este guia ajuda-te a configurar e executar o Multi-Agent Trading Framework pela primeira vez.

Instalação
----------

1. Clona o repositório.
2. Cria um ambiente virtual: ``python -m venv .venv``.
3. Ativa o ambiente: ``source .venv/bin/activate`` (Linux/Mac) ou ``.venv\Scripts\activate`` (Windows).
4. Instala as dependências: ``pip install -r requirements.txt``.

Execução Básica
---------------

Para correr um backtest de exemplo:

.. code-block:: bash

   python examples/backtest_example.py

Interface Visual
----------------

O MATF inclui um Dashboard Streamlit para monitorização:

.. code-block:: bash

   streamlit run multiagent_trading/analytics/dashboard.py

Utilização da CLI
-----------------

Podes gerir o framework através da linha de comandos:

.. code-block:: bash

   python multiagent_trading/utils/cli.py dashboard
   python multiagent_trading/utils/cli.py api

Configuração de Agentes
-----------------------

As estratégias são definidas em ficheiros JSON na pasta ``strategies/``. Podes usar o **Strategy Builder** no Dashboard para criar as tuas próprias combinações de agentes.
