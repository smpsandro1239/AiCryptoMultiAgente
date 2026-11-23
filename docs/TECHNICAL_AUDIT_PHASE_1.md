# Auditoria técnica — fase 1

**Repositório:** AiCryptoMultiAgente  
**Âmbito:** leitura estática dos módulos de orquestração, agentes base, memória, configuração, carregamento de dados e exemplo de backtest.  
**Data:** 2026-11-23  
**Classificação:** protótipo experimental; não aprovado para capital real.

## Resumo executivo

A estrutura multiagente é uma base de exploração válida, mas o comportamento atual é sobretudo demonstrativo. A existência de nomes como RiskAgent, LLMAgent ou Backtester não significa que exista, respetivamente, avaliação quantitativa de risco, inferência por modelo ou simulação financeira realista.

## Constatações

| ID | Severidade | Evidência | Risco |
|---|---|---|---|
| MATF-001 | Crítica | `ExecutionAgent` soma um valor fixo ao portefólio | Resultados de simulação sem significado financeiro |
| MATF-002 | Alta | `RiskAgent` define `risk_ok=True` | Oportunidades aprovadas sem limites de risco |
| MATF-003 | Alta | `RegimeAgent` define sempre `BULL` | Decisões dependentes de regime enviesadas |
| MATF-004 | Alta | `LLMAgent` constrói texto determinístico | Aparência de raciocínio IA sem inferência real |
| MATF-005 | Alta | `Backtester` apenas regista `portfolio.total_value` | Ausência de fills, fees, slippage, funding e métricas |
| MATF-006 | Média | `load_ohlcv_csv` devolve dados fictícios se o ficheiro não existir | Um backtest pode aparentar sucesso sem dados reais |
| MATF-007 | Média | `EventBus` original assumia callbacks awaitable | Callbacks síncronos poderiam falhar em runtime |
| MATF-008 | Média | Dependências declaradas de forma divergente entre `requirements.txt` e `pyproject.toml` | Instalações não reproduzíveis |

## Alterações desta fase

- EventBus passou a aceitar callbacks síncronos e assíncronos.
- Adicionado `unsubscribe`, com retorno booleano.
- O dispatcher usa uma cópia dos subscritores durante cada publicação.
- O contexto preserva objetos de memória explicitamente fornecidos, mesmo que sejam falsy.
- Adicionados testes de unidade para publicação, remoção de subscritores, contexto e backtest.
- Configurados pytest, Ruff e dependências opcionais de desenvolvimento.
- Adicionado GitHub Actions para executar testes e lint.
- README revisto para declarar limitações e separar protótipo de sistema de produção.

## Limitações que permanecem abertas

1. O carregador CSV ainda cria dados fictícios quando o ficheiro não existe. Deve ser alterado para falhar por omissão e só gerar dados sintéticos quando explicitamente solicitado.
2. Os agentes de regime, scanner, risco, supervisor, LLM e execução continuam a conter lógica demonstrativa.
3. A memória SQLite não tem ainda política de retenção, migrações, controlo de concorrência ou validação de payloads.
4. Não foi possível executar os testes no ambiente remoto desta auditoria. O CI foi preparado, mas o resultado só poderá ser confirmado após execução no GitHub Actions.
5. Não foi realizada análise dinâmica de todas as integrações, nem auditoria de dependências/transitivas ou teste de segurança a credenciais.

## Critérios para considerar uma futura versão apta a paper trading

- Dados OHLCV validados e sem fallback silencioso.
- Simulador de ordens com fees, slippage, latência e rejeições.
- Contabilidade de posições e PnL realizado/não realizado.
- Limites de exposição, sizing, stop-loss, drawdown e circuit breaker.
- Testes de integração e cenários de falha.
- Segredos fora do código e integração apenas com sandbox por omissão.
- Registos auditáveis e reconciliação entre ordens, fills e portefólio.

## Conclusão

A fase 1 melhora a fiabilidade do núcleo e a transparência documental. Não elimina as limitações de estratégia, risco e execução identificadas. A próxima fase deve começar pela validação de dados e pela remoção do fallback silencioso para dados sintéticos.
