from multiagent_trading.agents.base import BaseAgent

import asyncio
import time

class ExecutionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)
        self.event_bus.subscribe("emergency_panic", self.on_emergency_panic)
        self.war_mode = False

    async def on_emergency_panic(self, data):
        self.war_mode = True
        self.logger.error("Emergência recebida no ExecutionAgent. A fechar todas as posições!")
        # Lógica para fechar posições reais ou simuladas
        if hasattr(self.context.portfolio, "positions"):
            symbols = list(self.context.portfolio.positions.keys())
            for symbol in symbols:
                await self._execute_market({"symbol": symbol, "side": "SELL", "amount": "ALL"})
            self.context.portfolio.positions = {}

    async def on_trade_approved(self, opp):
        if self.war_mode:
            self.logger.warning(f"Troca para {opp['symbol']} bloqueada: MODO DE GUERRA ativo.")
            return
        strategy = opp.get("execution_strategy", "MARKET")
        self.logger.info(f"{self.name} a iniciar execução {strategy} para {opp['symbol']}...")

        if strategy == "TWAP":
            await self._execute_twap(opp)
        elif strategy == "VWAP":
            await self._execute_vwap(opp)
        elif strategy == "OCO":
            await self._execute_oco(opp)
        elif strategy == "LIMIT":
            await self._execute_limit(opp)
        else:
            await self._execute_market(opp)

        # Atualizar portfólio e memória
        self.context.portfolio.total_value += 10 # Simular lucro
        opp["timestamp"] = time.time() # Key standard para o visualizador
        opp["execution_timestamp"] = opp["timestamp"]
        self.context.memory.add("trade", opp)

    async def _execute_market(self, opp):
        self.logger.info(f"Execução MARKET concluída para {opp['symbol']}")

    async def _execute_twap(self, opp):
        intervals = 5
        self.logger.info(f"A iniciar TWAP em {intervals} intervalos para {opp['symbol']}")
        for i in range(intervals):
            await asyncio.sleep(0.1) # Simulação de espera entre fatias
            self.logger.info(f"TWAP: Slice {i+1}/{intervals} executada")
        self.logger.info(f"Execução TWAP concluída para {opp['symbol']}")

    async def _execute_vwap(self, opp):
        # Em cenário real, basear-se-ia no perfil de volume intradiário
        self.logger.info(f"Execução VWAP concluída para {opp['symbol']} (baseada em volume simulado)")

    async def _execute_oco(self, opp):
        # Ordem Cancels Other: Take Profit e Stop Loss simultâneos
        self.logger.info(f"Ordem OCO colocada para {opp['symbol']}: TP {opp.get('tp')} | SL {opp.get('sl')}")
        self.logger.info(f"Execução OCO concluída para {opp['symbol']}")

    async def _execute_limit(self, opp):
        self.logger.info(f"Ordem LIMIT colocada para {opp['symbol']} ao preço {opp.get('price')}")
        self.logger.info(f"Execução LIMIT concluída para {opp['symbol']}")
