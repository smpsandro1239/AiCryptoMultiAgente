# Fase 2 — Risk Engine e Portfolio Manager

## Âmbito

Esta fase introduz contabilidade determinística de portefólio e uma barreira independente de pré-negociação. Os componentes são locais e destinam-se exclusivamente a simulação/paper trading. Não existe submissão de ordens a exchanges.

## Risk Engine

O RiskEngine recebe uma intenção com symbol, side, entry_price e stop_price e o estado do portefólio. Ignora deliberadamente qualquer campo risk_ok fornecido por agentes. A decisão RiskDecision contém quantidade, notional, risco estimado e motivos de rejeição.

Limites configuráveis: risco máximo por trade, notional máximo por ordem, fração máxima por posição, exposição agregada máxima, perda diária máxima e distância mínima ao stop. Dados inválidos ou estado inconsistente resultam em rejeição (fail closed).

O sizing é baseado na distância ao stop e limitado pelo saldo disponível e limites de exposição. Ainda não considera volatilidade, correlação, liquidez, concentração por ativo correlacionado, funding, slippage ou risco de execução.

## Portfolio Manager / PortfolioState

PortfolioState mantém cash, posições spot líquidas, preço de marcação, preço médio ponderado, PnL realizado/não realizado e comissões. apply_fill() representa um fill simulado e valida saldo, quantidade, preço, comissão e inventário antes de alterar o estado.

Não há persistência transacional, reconciliação com exchange, ordens parciais, shorting, margem, derivados, empréstimos ou funding.

## Limites de segurança

- Nenhum agente deve converter uma recomendação diretamente numa ordem.
- A decisão de risco deve ser recalculada na fronteira de execução, com dados atuais.
- O RiskEngine não executa ordens; apenas calcula uma decisão.
- O código desta fase não liga a exchanges nem ativa trading real.
- Os testes validam regras contabilísticas e limites, não rentabilidade de estratégias.

## Próximos passos

1. Ligar o pipeline de agentes a um serviço de aprovação de risco sem confiar em risk_ok.
2. Introduzir Order/Fill imutáveis, idempotência e estados de ordem.
3. Adicionar drawdown por equity curve e limites por sessão.
4. Modelar comissões, slippage e funding no backtester.
5. Adicionar property-based tests e testes de concorrência.
