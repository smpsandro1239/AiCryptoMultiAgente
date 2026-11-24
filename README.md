# Multi-Agent Trading Framework (MATF)

Framework experimental de trading multiagente, orientado a eventos e desenvolvido em Python.

> **Estado atual: protótipo de investigação e paper trading.** A branch de modernização introduz um motor de risco independente e contabilidade simulada de portefólio, mas os agentes de mercado e o backtester continuam parcialmente demonstrativos. Não utilizar com capital real nem interpretar mensagens geradas como recomendações financeiras.

## Objetivos

- Separar responsabilidades por agentes especializados.
- Coordenar agentes através de um barramento assíncrono de eventos.
- Exigir aprovação independente de risco antes de qualquer fill simulado.
- Manter contabilidade auditável de posições, capital, PnL e comissões.
- Criar uma base testável para simulação e investigação quantitativa.

## Estado funcional conhecido

| Componente | Estado observado | Limitação relevante |
|---|---|---|
| EventBus | Implementado | Dispatcher em memória; sem persistência ou garantias de entrega |
| Orchestrator | Implementado | Atualiza contexto e publica eventos |
| RegimeAgent | Protótipo | Define o regime como BULL sem análise quantitativa |
| ScannerAgent | Protótipo | Emite oportunidade demonstrativa; não calcula sinal/stop completos |
| RiskEngine | Primeira implementação | Sizing por distância ao stop, comissões estimadas, notional/exposição, perda diária e drawdown; ainda sem volatilidade, correlação ou liquidez |
| RiskAgent | Integrado nesta fase | Partilha o RiskEngine injetado no Context; rejeita dados incompletos e ignora risk_ok |
| PortfolioState / PortfolioStore | Implementado para simulação | Posições spot, preço médio incluindo taxas, cash, PnL, comissões, high-water mark e snapshots SQLite versionados; persistência ainda explícita, sem transação comum com o ledger de ordens |
| SupervisorAgent | Protegido por decisão explícita | Só inicia raciocínio e aprova quando risk_decision.approved é true |
| LLMAgent | Simulação | Produz texto determinístico; não consulta um modelo LLM |
| ExecutionAgent | Paper-only | Revalida risco, usa ledger SQLite opcional para idempotência e aplica fills simulados; sem exchange |
| Backtester | Básico | Regista valor do portefólio; ainda não modela fills históricos, slippage, funding ou latência |

As funcionalidades descritas como primeira implementação não representam certificação, validação de rentabilidade ou prontidão para produção. Consultar docs/PHASE_2_RISK_PORTFOLIO.md, docs/PHASE_3_PORTFOLIO_PERSISTENCE.md e docs/TECHNICAL_AUDIT_PHASE_1.md.

## Arquitetura de segurança

~~~mermaid
flowchart TD
    DATA[Market Data] --> INTEL[Market Intelligence]
    INTEL --> STRAT[Strategy Agents]
    STRAT --> RISK[Independent Risk Engine]
    RISK --> DEC{Risk Approved?}
    DEC -->|No| REJECT[Reject Trade]
    DEC -->|Yes| SUP[Supervisor / LLM reasoning]
    SUP --> GATE[Execution Risk Revalidation]
    GATE --> PAPER[Paper Execution]
    PAPER --> FILL[Simulated Fill]
    FILL --> PORT[Portfolio Accounting]
    PORT --> MEM[Audit Memory]
~~~

O campo risk_ok fornecido por um agente não autoriza uma operação. O RiskEngine valida os dados e o estado do portefólio, e o ExecutionAgent volta a calcular o risco imediatamente antes do fill simulado. A ausência de preço, stop ou portefólio válido resulta em rejeição.

## Requisitos

- Python 3.10 ou superior.
- Git.
- Dependências Python declaradas em pyproject.toml.

## Instalação

~~~bash
git clone https://github.com/smpsandro1239/AiCryptoMultiAgente.git
cd AiCryptoMultiAgente
python -m venv .venv
~~~

Ativar o ambiente virtual:

**Linux/macOS**
~~~bash
source .venv/bin/activate
~~~

**Windows PowerShell**
~~~powershell
.venv\Scripts\Activate.ps1
~~~

Instalar dependências e ferramentas de desenvolvimento:

~~~bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

## Testes e qualidade

~~~bash
pytest
ruff check .
ruff format --check .
~~~

O pipeline de CI executa testes e verificações de lint. A aprovação do CI não equivale a validação de uma estratégia de trading nem a prova de rentabilidade.

## Executar o exemplo

~~~bash
python examples/backtest_example.py
~~~

O exemplo atual demonstra o fluxo de eventos e não constitui um backtest financeiro fiável.

## Segurança

- Nunca guardar API keys, passwords ou tokens no repositório.
- Nunca ativar negociação real com esta versão experimental.
- Não permitir que agentes de estratégia contornem o RiskEngine.
- Revalidar risco no ponto de execução.
- Usar contas sandbox/testnet e permissões mínimas se forem adicionadas integrações futuras.
- Não ativar permissões de levantamento nas chaves de API.
- Validar dados OHLCV, timestamps, duplicados e valores inválidos antes de qualquer análise.
- Consultar SECURITY.md para o processo de reporte.

## Roadmap

- [x] Documentar o estado real dos agentes e do simulador.
- [x] Melhorar o EventBus e adicionar testes de unidade.
- [x] Introduzir CI para testes e lint.
- [x] Validar candles CSV e rejeitar dados ausentes por omissão.
- [x] Introduzir RiskEngine com sizing e limites de exposição.
- [x] Introduzir contabilidade de portefólio e fills simulados.
- [x] Exigir aprovação de risco no fluxo de agentes e revalidar antes do fill.
- [x] Implementar circuit breaker por perda diária e drawdown com high-water mark em memória.
- [x] Persistir snapshots versionados do portefólio em SQLite e restaurar estado contabilístico validado.\n- [ ] Persistir equity curve completa e definir limites diários a partir do equity de início do dia.
- [x] Adicionar ledger SQLite de ordens com IDs únicos e bloqueio fail-closed de ordens pendentes após reinício.
- [ ] Integrar snapshots automaticamente no ciclo de execução e reconciliar ordens pending após crash, com consistência transacional entre ledger e portefólio.
- [ ] Modelar comissões, slippage, funding e latência no backtester.
- [ ] Normalizar fusos horários, ordenação temporal e gaps.
- [ ] Implementar classificação quantitativa de regime e scanner real.
- [ ] Adicionar integração de LLM real com limites e avaliação.
- [ ] Considerar exchange sandbox apenas após auditoria e testes adicionais.

## Licença

MIT — consultar o ficheiro LICENSE.
