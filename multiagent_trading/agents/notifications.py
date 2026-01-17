from multiagent_trading.agents.base import BaseAgent

class NotificationAgent(BaseAgent):
    """
    Handles outbound notifications to external services like Discord or Telegram.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)
        self.event_bus.subscribe("regime_change", self.on_regime_change)

    async def on_trade_approved(self, opp):
        msg = f"🚀 Trade Approved: {opp['side']} {opp['symbol']} @ size {opp.get('optimized_size', 'N/A')}"
        self.send_notification(msg)

    async def on_regime_change(self, regime):
        msg = f"🔄 Market Regime Change detected: {regime}"
        self.send_notification(msg)

    def send_notification(self, message):
        # In a real scenario, this would use 'requests' to post to a webhook
        # self.logger.info(f"NOTIFICATION [MOCK]: {message}")

        # Store in memory for visibility in dashboard
        self.context.memory.add("notification", message)
        self.logger.info(f"{self.name} notification sent: {message}")
