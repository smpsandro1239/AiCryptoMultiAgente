# Portfolio Persistence — Fase 3

## Objetivo

Introduzir persistência explícita do estado contabilístico de paper trading,
sem confundir snapshots com execução transacional de ordens.

## Implementação

- `PortfolioStore` grava snapshots completos em SQLite.
- Cada gravação é append-only e usa uma transação SQLite explícita.
- SQLite usa WAL e `synchronous=FULL` em bases de dados em disco.
- Os snapshots incluem capital inicial, saldo, posições, preços de marcação,
  comissões, PnL e high-water mark.
- Cada registo tem uma versão de schema; versões desconhecidas são rejeitadas.
- `PortfolioState.from_snapshot()` valida os dados antes de reconstruir o estado.
- O histórico expõe metadados sem descodificar os snapshots.

## Utilização

```python
from multiagent_trading.core.portfolio_store import PortfolioStore
from multiagent_trading.models.portfolio import PortfolioState

store = PortfolioStore("data/portfolio.sqlite3")
portfolio = store.load_latest() or PortfolioState(initial_value=10_000)

# Depois de uma alteração contabilística confirmada:
store.save(portfolio)
store.close()
```

## Limites conhecidos

Esta camada não está ainda ligada automaticamente ao ciclo de execução. A
aplicação tem de chamar `save()` depois de cada alteração contabilística
confirmada e `load_latest()` no arranque. A gravação do snapshot e a atualização
do ledger de ordens não constituem uma transação única. Uma falha entre estas
operações pode exigir reconciliação manual; ordens pendentes continuam a ser
tratadas em modo fail-closed.

A funcionalidade continua limitada a paper trading. Não envia ordens reais
para exchanges e não deve ser usada como sistema contabilístico de produção.
