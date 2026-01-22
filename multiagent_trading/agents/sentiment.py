from multiagent_trading.agents.base import BaseAgent
import random

class SentimentAgent(BaseAgent):
    """
    Agente que simula análise de sentimento de notícias e redes sociais.
    Publica eventos de mudanças de sentimento que afetam as decisões.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("news_article", self.on_news)

    async def on_news(self, news):
        headline = news.get("headline")
        symbol = news.get("symbol")

        # Simulação de análise de NLP simplificada
        sentiment_score = random.uniform(-1, 1)
        if "máximo" in headline or "adoção" in headline:
            sentiment_score = abs(sentiment_score) # Positivo
        elif "queda" in headline or "regulação" in headline:
            sentiment_score = -abs(sentiment_score) # Negativo

        await self._publish_sentiment(symbol, sentiment_score)

    async def on_market_update(self, data):
        # Continua a gerar sentimento baseado no ruído de mercado
        symbol = data.get("symbol")
        sentiment_score = random.uniform(-1, 1)

        if abs(sentiment_score) > 0.7: # Apenas ruído forte
            await self._publish_sentiment(symbol, sentiment_score)

    async def _publish_sentiment(self, symbol, sentiment_score):
            sentiment_label = "BULLISH" if sentiment_score > 0 else "BEARISH"
            self.logger.info(f"Sentimento detectado para {symbol}: {sentiment_label}", score=sentiment_score)

            await self.event_bus.publish("sentiment_shift", {
                "symbol": symbol,
                "score": sentiment_score,
                "label": sentiment_label
            })
