import random
from multiagent_trading.agents.base import BaseAgent

class SentimentAgent(BaseAgent):
    """
    Simulates an agent that analyzes market sentiment from news feeds and social media.
    """
    async def on_market_update(self, data_batch):
        if not data_batch:
            return

        self.logger.info(f"{self.name} analyzing social sentiment...")

        # In a real implementation, this would call an LLM or use a NLP library
        # to process news headlines or tweets for the symbols in data_batch.

        for symbol in data_batch.keys():
            # Mock sentiment score between -1 (very bearish) and 1 (very bullish)
            sentiment_score = random.uniform(-1, 1)

            self.logger.info(f"Sentiment for {symbol}: {sentiment_score:.2f}")

            # Store sentiment in context
            if not hasattr(self.context, 'sentiment'):
                self.context.sentiment = {}

            self.context.sentiment[symbol] = sentiment_score

            # Publish event if sentiment is extreme
            if sentiment_score > 0.8:
                await self.event_bus.publish("high_bullish_sentiment", {"symbol": symbol, "score": sentiment_score})
            elif sentiment_score < -0.8:
                await self.event_bus.publish("high_bearish_sentiment", {"symbol": symbol, "score": sentiment_score})
