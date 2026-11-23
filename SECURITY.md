# Política de Segurança

## Âmbito

Este projeto é experimental e não está aprovado para negociação com capital real.

## Reportar vulnerabilidades

Não publiques credenciais, tokens, chaves de API ou detalhes exploráveis em issues públicas. Para reportar uma vulnerabilidade, utiliza os canais privados de reporte de segurança disponibilizados pelo GitHub para este repositório.

## Regras de segurança

- Não guardar segredos em ficheiros versionados.
- Usar variáveis de ambiente ou um gestor de segredos.
- Utilizar chaves de exchange com permissões mínimas.
- Desativar levantamentos nas chaves de API.
- Manter negociação live desativada por omissão.
- Utilizar sandbox/testnet durante desenvolvimento.
- Nunca assumir que o sinal de um agente constitui autorização suficiente para executar uma ordem.
- Registar decisões de risco, pedidos, respostas e falhas sem expor segredos.

## Resposta a incidentes

Perante suspeita de exposição de uma chave: revogar imediatamente a chave na exchange, verificar atividade e ordens, rodar segredos relacionados e preservar logs relevantes.
