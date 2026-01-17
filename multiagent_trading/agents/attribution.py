from multiagent_trading.agents.base import BaseAgent

class PerformanceAttributionAgent(BaseAgent):
    """
    Analyzes and attributes PnL to different factors (Strategy, Regime, Market).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pnl_by_factor = {"Strategy": 0, "Regime": 0, "Sentiment": 0}

    async def on_market_update(self, data_batch):
        # Triggered when trades are executed
        executions = self.context.memory.get_by_key("execution")
        if not executions: return

        last_exec = executions[-1]["value"]
        pnl = last_exec.get("pnl", 0)

        # Attribution Logic (Simplistic)
        # Attribute PnL based on the current regime and sentiment at the time of trade
        regime = self.context.regime
        sentiment = 0
        if hasattr(self.context, 'sentiment'):
             symbol = last_exec.get("symbol")
             sentiment = self.context.sentiment.get(symbol, 0)

        # Attribution heuristic
        if regime == "BULL" and last_exec["side"] == "BUY":
            self.pnl_by_factor["Regime"] += pnl * 0.4
            self.pnl_by_factor["Strategy"] += pnl * 0.6
        elif abs(sentiment) > 0.5:
            self.pnl_by_factor["Sentiment"] += pnl * 0.5
            self.pnl_by_factor["Strategy"] += pnl * 0.5
        else:
            self.pnl_by_factor["Strategy"] += pnl

        self.context.memory.add("pnl_attribution", self.pnl_by_factor.copy())
        self.logger.info(f"{self.name} Updated PnL Attribution: {self.pnl_by_factor}")
