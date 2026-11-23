# Fase 2 — Risk Engine e Portfolio Manager

## Implementação

Esta fase introduz contabilidade determinística de portefólio e uma barreira independente de pré-negociação. Tudo é local e exclusivamente destinado a paper trading; não existe submissão de ordens a exchanges.

### Risk Engine

O RiskEngine recebe uma intenção com symbol, side, entry_price e stop_price e o estado do portefólio. Ignora qualquer campo risk_ok fornecido por agentes. A decisão RiskDecision contém aprovação, quantidade, notional, risco estimado e motivos de rejeição.

Limites configuráveis: risco máximo por trade, notional máximo por ordem, fração máxima por posição, exposição agregada máxima, perda diária máxima, drawdown máximo, distância mínima ao stop e comissão estimada. O mesmo RiskEngine pode ser injetado em Context(risk_engine=...) e é partilhado pelo RiskAgent e pelo ExecutionAgent. Dados inválidos, stop ausente ou estado inconsistente resultam em rejeição (fail closed).

O sizing é baseado na distância ao stop e limitado pelo saldo, comissão estimada e limites de exposição. A PortfolioState mantém o high-water mark e calcula o drawdown corrente. Ao atingir o limite de perda diária ou drawdown, novas entradas são bloqueadas, mas as vendas de redução/fecho de posições existentes continuam permitidas. Ainda não considera volatilidade, correlação, liquidez, funding, slippage ou risco de execução.

### Pipeline de agentes

O fluxo está ligado nesta branch:
1. RiskAgent recebe opportunity_found e calcula uma decisão independente.
2. Apenas decisões explicitamente aprovadas publicam risk_assessed.
3. SupervisorAgent exige risk_decision.approved == true antes de solicitar raciocínio.
4. SupervisorAgent volta a verificar a decisão antes de publicar trade_approved.
5. ExecutionAgent recalcula o risco imediatamente antes do fill e rejeita duplicados na sessão.
6. Só depois aplica um fill simulado, persiste o estado final da ordem e publica paper_fill.

A ausência de entry_price, stop_price ou PortfolioState válido bloqueia a operação. O campo risk_ok enviado pela estratégia não concede autorização.

### Portfolio Manager

OrderStore mantém um ledger SQLite com identificador único e estados pending/filled/rejected. O caminho é configurável por order_db_path; por omissão usa SQLite em memória para não criar ficheiros inesperados em testes. Uma ordem deixada em pending por uma interrupção não é repetida automaticamente (fail closed).\n\nPortfolioState mantém cash, posições spot líquidas, preço médio ponderado incluindo comissão de entrada, marcação a mercado, PnL realizado/não realizado, comissões e high-water mark. apply_fill() valida saldo, inventário, quantidade, preço, comissão e resultados numéricos finitos antes de modificar o estado. Os fills são simulados; não são ordens de exchange.

### Limitações conhecidas

- O ledger de ordens suporta persistência SQLite quando order_db_path aponta para um ficheiro, mas o portefólio continua em memória; não existe ainda transação atómica entre ledger e contabilidade. Ordens pending após crash ficam bloqueadas para reconciliação manual.
- O estado do portefólio ainda não tem persistência transacional nem reconciliação externa.
- Não existem ordens parciais, shorting, margem, derivados, empréstimos ou funding.
- O controlo diário usa daily_pnl fornecido pelo contexto; o high-water mark e o circuito de drawdown são mantidos apenas em memória e ainda não têm equity curve persistente.
- A configuração única pode ser injetada no Context; falta carregá-la de configuração validada e protegida por ambiente.
- O scanner demonstrativo não fornece preços/stop por si; oportunidades sem esses dados são corretamente rejeitadas.
- Não há integração de trading real nem deve ser adicionada antes de auditoria independente.

## Próximos passos

1. Persistir high-water mark/equity curve e definir limites diários a partir do equity de início do dia.
2. Persistir o estado do portefólio e implementar reconciliação de ordens pending após crash.
3. Modelar comissões, slippage e funding no backtester.
4. Adicionar testes de propriedades, concorrência e recuperação após reinício.
5. Validar todos os agentes e exemplos com CI antes de remover o estado Draft da PR.
