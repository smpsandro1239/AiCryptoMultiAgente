import asyncio
import json
import pandas as pd
from typing import Dict, Any, List
from multiagent_trading.core.logger import Logger
from multiagent_trading.core.memory import PersistentSemanticMemory
from multiagent_trading.analytics.metrics import calculate_sharpe_ratio, calculate_max_drawdown

class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type: str, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    async def publish(self, event_type: str, data: Any):
        if event_type in self.listeners:
            tasks = [callback(data) for callback in self.listeners[event_type]]
            await asyncio.gather(*tasks)

class Context:
    def __init__(self, timestamp=None, regime=None, portfolio=None, market_data=None, memory=None):
        self.timestamp = timestamp
        self.regime = regime
        self.portfolio = portfolio
        self.market_data = market_data
        self.memory = memory or PersistentSemanticMemory()

class Orchestrator:
    def __init__(self, agents, context, event_bus, logger):
        self.agents = agents
        self.context = context
        self.event_bus = event_bus
        self.logger = logger

    async def step(self, market_snapshot: Dict[str, Any]):
        """
        snapshot pode ser um único tick ou um dicionário {symbol: tick_data}
        """
        self.context.market_data = market_snapshot

        # Se for multi-símbolo, extrair timestamp de um deles
        if isinstance(market_snapshot, dict) and "timestamp" not in market_snapshot and market_snapshot:
            first_val = next(iter(market_snapshot.values()))
            if isinstance(first_val, dict):
                self.context.timestamp = first_val.get("timestamp")
        else:
            self.context.timestamp = market_snapshot.get("timestamp")

        await self.event_bus.publish("market_update", market_snapshot)

class Backtester:
    def __init__(self, orchestrator, data_feed, context, commission=0.001, slippage=0.0005):
        self.orchestrator = orchestrator
        self.data_feed = data_feed
        self.context = context
        self.commission = commission # 0.1% por defeito
        self.slippage = slippage # 0.05% por defeito
        self.results = {"pnl": [], "memory": []}

        # Subscrever a eventos de trade para aplicar taxas
        self.orchestrator.event_bus.subscribe("trade_approved", self._apply_trading_costs)

    async def _apply_trading_costs(self, opp):
        """Aplica slippage e comissões ao portfólio no momento da aprovação do trade."""
        if hasattr(self.context.portfolio, "total_value"):
            # Simulação simplificada de custo baseada no valor da troca (ou valor fixo para o exemplo)
            trade_value = 1000 # Assumindo um tamanho de posição standard
            costs = trade_value * (self.commission + self.slippage)
            self.context.portfolio.total_value -= costs
            self.orchestrator.logger.info(f"Custos de trading aplicados: -{costs:.2f} (Comissão + Slippage)")

    async def run(self, save_path=None):
        pnl_history = []
        for tick in self.data_feed:
            await self.orchestrator.step(tick)
            val = self.context.portfolio.total_value
            self.results["pnl"].append(val)
            pnl_history.append(val)

        # Calcular métricas finais
        returns = pd.Series(pnl_history).pct_change().dropna().tolist()
        self.results["metrics"] = {
            "sharpe_ratio": calculate_sharpe_ratio(returns),
            "max_drawdown": calculate_max_drawdown(pnl_history),
            "final_value": self.context.portfolio.total_value
        }

        if save_path:
            self.save_results(save_path)

        return self.results

    def save_results(self, filepath):
        """Guarda os resultados e a memória semântica num ficheiro JSON."""
        # Tentar obter memória persistente se disponível
        if hasattr(self.context.memory, 'query'):
            self.results["memory"] = self.context.memory.query("")

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=4)

class LiveOrchestrator(Orchestrator):
    """
    Variante do Orchestrator otimizada para execução em tempo real com feeds de dados vivos.
    """
    def __init__(self, agents, context, event_bus, logger, adapter):
        super().__init__(agents, context, event_bus, logger)
        self.adapter = adapter
        self.running = False

    async def start(self, symbol, timeframe='1m'):
        """Inicia o loop de trading em tempo real."""
        self.running = True
        self.logger.info(f"A iniciar LiveOrchestrator para {symbol} ({timeframe})")

        async for tick in self.adapter.watch_ohlcv(symbol, timeframe):
            if not self.running:
                break

            # Normalizar tick para o formato esperado pelo orchestrator
            market_snapshot = {
                "symbol": symbol,
                "open": tick[1],
                "high": tick[2],
                "low": tick[3],
                "close": tick[4],
                "volume": tick[5],
                "timestamp": tick[0]
            }

            await self.step(market_snapshot)

    def stop(self):
        self.running = False
        self.logger.info("LiveOrchestrator parado.")
