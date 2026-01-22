from multiagent_trading.agents.base import BaseAgent
import random
import asyncio

class NewsAgent(BaseAgent):
    """
    Agente que simula um feed de notícias do mercado financeiro.
    Publica eventos de notícias que podem ser processados por agentes de sentimento.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.news_templates = [
            "{} atinge novo máximo histórico",
            "Relatório de inflação impacta o par {}",
            "Nova regulação para {} anunciada hoje",
            "Baleias movem grandes quantias de {}",
            "Analistas preveem queda acentuada para {}"
        ]

    async def on_market_update(self, data):
        # 10% de probabilidade de gerar uma notícia a cada tick
        if random.random() > 0.9:
            symbol = data.get("symbol", "BTC")
            headline = random.choice(self.news_templates).format(symbol)

            self.logger.info(f"Nova notícia gerada: {headline}")
            await self.event_bus.publish("news_article", {
                "headline": headline,
                "symbol": symbol,
                "timestamp": data.get("timestamp")
            })
