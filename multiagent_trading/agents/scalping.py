import asyncio
from multiagent_trading.agents.base import BaseAgent

class ScalpingAgent(BaseAgent):
    """
    Agente focado em Scalping e HFT.
    Analisa micro-tendências para execuções rápidas de entrada e saída.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tick_window = self.config.get("scalping", {}).get("window", 5)
        self.momentum_threshold = self.config.get("scalping", {}).get("threshold", 0.0005)

    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        self.logger.info(f"{self.name} a analisar micro-momentum para scalping...")

        for symbol, data in data_batch.items():
            if not hasattr(self, 'price_history'):
                self.price_history = {}

            if symbol not in self.price_history:
                self.price_history[symbol] = []

            self.price_history[symbol].append(data.get("close", 0))
            if len(self.price_history[symbol]) > self.tick_window:
                self.price_history[symbol].pop(0)

            if len(self.price_history[symbol]) < self.tick_window:
                continue

            # Calcular momentum simples de curto prazo
            start_price = self.price_history[symbol][0]
            current_price = self.price_history[symbol][-1]
            if start_price == 0: continue

            momentum = (current_price - start_price) / start_price

            if abs(momentum) > self.momentum_threshold:
                side = "BUY" if momentum > 0 else "SELL"
                self.logger.info(f"Oportunidade de Scalping em {symbol}: {side} (Momentum: {momentum:.4%})")

                # Emitir sinal para o barramento de eventos
                await self.event_bus.publish("opportunity_found", {
                    "symbol": symbol,
                    "side": side,
                    "reason": f"Scalping Micro-Momentum ({momentum:.4%})",
                    "price": current_price
                })
