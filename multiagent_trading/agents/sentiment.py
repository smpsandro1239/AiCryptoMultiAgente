from multiagent_trading.agents.base import BaseAgent
import random

class SentimentAgent(BaseAgent):
    """
    Agente que simula análise de sentimento de notícias e redes sociais.
    Publica eventos de mudanças de sentimento que afetam as decisões.
    """
    async def on_market_update(self, data):
        symbol = data.get("symbol")

        # Simulação de análise de sentimento
        # Em produção, integraria com APIs de NLP ou feeds de notícias
        sentiment_score = random.uniform(-1, 1) # -1 (Negativo) a 1 (Positivo)

        if abs(sentiment_score) > 0.5:
            sentiment_label = "BULLISH" if sentiment_score > 0 else "BEARISH"
            self.logger.info(f"Sentimento detectado para {symbol}: {sentiment_label}", score=sentiment_score)

            await self.event_bus.publish("sentiment_shift", {
                "symbol": symbol,
                "score": sentiment_score,
                "label": sentiment_label
            })
