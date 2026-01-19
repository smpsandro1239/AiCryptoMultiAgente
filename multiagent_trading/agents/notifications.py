from multiagent_trading.agents.base import BaseAgent
import requests

class NotificationAgent(BaseAgent):
    """
    Agente que gere notificações externas (Webhooks, etc.) para aprovações de trocas e mudanças de regime.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webhook_url = self.config.get("webhook_url")
        self.event_bus.subscribe("trade_approved", self.on_trade_approved)
        self.event_bus.subscribe("regime_change", self.on_regime_change)

    async def on_trade_approved(self, opp):
        msg = f"🚀 Negociação aprovada: {opp.get('side')} {opp.get('symbol')}"
        self.logger.info(f"A enviar notificação: {msg}")
        await self._send_notification(msg)

    async def on_regime_change(self, regime):
        msg = f"🔄 Mudança de regime detectada: {regime}"
        self.logger.info(f"A enviar notificação: {msg}")
        await self._send_notification(msg)

    async def _send_notification(self, message):
        if self.webhook_url:
            try:
                # Simulação de envio asíncrono
                # requests.post(self.webhook_url, json={"text": message})
                pass
            except Exception as e:
                self.logger.error(f"Erro ao enviar notificação: {str(e)}")
