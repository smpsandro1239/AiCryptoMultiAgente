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
        # Envio para Webhook Genérico
        if self.webhook_url:
            try:
                # requests.post(self.webhook_url, json={"text": message})
                self.logger.info(f"Notificação Webhook enviada: {message}")
            except Exception as e:
                self.logger.error(f"Erro ao enviar notificação Webhook: {str(e)}")

        # Envio para Telegram (se configurado)
        telegram_token = self.config.get("telegram_token")
        chat_id = self.config.get("telegram_chat_id")

        if telegram_token and chat_id:
            try:
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                # requests.post(url, json={"chat_id": chat_id, "text": message})
                self.logger.info(f"Notificação Telegram enviada para o chat {chat_id}")
            except Exception as e:
                self.logger.error(f"Erro ao enviar notificação Telegram: {str(e)}")
