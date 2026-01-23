# 📋 Plano de Tarefas - MATF (Multi-Agent Trading Framework)

Este ficheiro regista o progresso detalhado do desenvolvimento.

**Progresso Total: 50 de 60 tarefas concluídas (83%)**

---

## ✅ Concluído (v0.6 - v1.3)

### Core & Infraestrutura
1. [x] Refatoração de Agentes para ficheiros individuais.
2. [x] Implementação de `EventBus` assíncrono.
3. [x] Logger estruturado JSON com `JsonFormatter`.
4. [x] Memória Persistente SQLite (`PersistentSemanticMemory`).
5. [x] `VectorMemory` para embeddings de regime com distância Euclidiana.
6. [x] CLI de gestão (`matf-cli`).
7. [x] Suporte para Docker e `docker-compose`.
8. [x] Estrutura de documentação Sphinx.
9. [x] Sistema de Plugins para carregamento dinâmico de agentes.
10. [x] `StrategyManager` e `StrategyBuilder` para gestão de configs.
11. [x] `SecurityManager` com Criptografia AES (Fernet).

### Agentes de Inteligência & Estratégia
12. [x] `RegimeClassifierAgent` (ML - Random Forest) com Online Learning.
13. [x] `RLAgent` (Reinforcement Learning - Q-Learning).
14. [x] `LLMAgent` para raciocínio qualitativo.
15. [x] `SentimentAgent` integrado com `NewsAgent`.
16. [x] `MicrostructureAgent` (Análise de Order Book).
17. [x] `ArbitrageAgent` (Mock de discrepância entre exchanges).
18. [x] `MarketMakerAgent` (Simulação de liquidez).
19. [x] `ScalpingAgent` (Micro-momentum).
20. [x] `DeFiAgent` com APY dinâmico e scores de risco.
21. [x] `MultiTimeframeScannerAgent` para confirmação de tendências.

### Gestão de Risco & Portfólio
22. [x] `RiskAgent` base.
23. [x] `SupervisorAgent` com aprovação baseada em votação Ensemble.
24. [x] `RiskParityOptimizerAgent` (Alocação por volatilidade).
25. [x] `MVOOptimizerAgent` (Mean-Variance Optimization).
26. [x] `BlackLittermanAgent` com visões dinâmicas de sentimento.
27. [x] `StopLossTakeProfitAgent`.
28. [x] `LongShortRebalancingAgent`.
29. [x] `RiskAnalysisAgent` com Monte Carlo e VaR.
30. [x] `MultiPortfolioManager` para sub-contas.

### Analytics & Execução
31. [x] `ExecutionAgent` (MARKET, TWAP, VWAP, OCO, LIMIT).
32. [x] `CCXTAdapter` com suporte a `watch_ohlcv` e `watch_trades`.
33. [x] `Backtester` com modelação de Slippage e Comissões.
34. [x] `BacktestOptimizer` (Grid Search de parâmetros).
35. [x] `PerformanceAttributionAgent` (PnL Attribution).
36. [x] Módulo de métricas: Sharpe, Sortino, MDD, Calmar, Treynor.
37. [x] `TradeVisualizer` (Plotly) integrado no Dashboard.
38. [x] Dashboard Streamlit com 11 abas funcionais.
39. [x] API REST FastAPI completa.
40. [x] Notificações via Telegram e Webhooks.

---

## 🏗️ Em Realização (Fase Atual: v1.3 -> v1.4)
41. [ ] **Monitorização de Saúde dos Agentes (Heartbeats)**
    - Implementar sistema de check-in para garantir que nenhum agente "morreu" em runtime.
42. [ ] **Integração Real de WebSockets no CCXTAdapter**
    - Substituir os mocks de `watch_trades` por chamadas reais via `ccxt.pro` (onde disponível).

---

## 🚀 Próximas Tarefas (v1.4 - v2.0)
43. [ ] Implementação de `LLMAgent` com RAG (Retrieval-Augmented Generation) para ler PDFs de research.
44. [ ] Sistema de Auto-Heal (Reiniciar agentes que falham automaticamente).
45. [ ] Visualização de Múltiplos Portfólios em simultâneo no Dashboard.
46. [ ] Templates de Deployment Cloud (Terraform para AWS/GCP).
47. [ ] Implementação de um "Modo de Guerra" (Botão de pânico que fecha todas as posições).
48. [ ] Relatórios PDF gerados automaticamente via Dashboard.
49. [ ] Suporte para Opções e Futuros no `ExecutionAgent`.
50. [ ] Agente de Arbitragem Estatística (Pairs Trading).
51. [ ] Melhoria do `RLAgent` para Deep Q-Learning (DQN).
52. [ ] Interface de chat no Dashboard para falar com o `LLMAgent`.
53. [ ] Exportação de logs para ELK Stack ou Grafana Loki.
54. [ ] Auditoria de latência entre eventos (Profiling).
55. [ ] Suporte para multi-moeda de conta (USD, EUR, BTC).
56. [ ] Agente de Governança (Votação para mudar parâmetros globais).
57. [ ] Documentação "Get Started" em vídeo/tutorial interativo.
58. [ ] Suite de testes de stress de latência (1000+ agentes).
59. [ ] Integração com Hardware Wallets para aprovação de saques (Segurança fria).
60. [ ] Versão Mobile-Friendly do Dashboard.
