import os
from typing import Dict

class SecurityManager:
    """
    Gere chaves de API e segredos utilizando variáveis de ambiente para maior segurança.
    """
    def __init__(self):
        self.keys = {}

    def load_exchange_keys(self, exchange_id: str) -> Dict[str, str]:
        """
        Carrega as chaves para uma exchange específica a partir do ambiente.
        """
        api_key = os.getenv(f"{exchange_id.upper()}_API_KEY")
        api_secret = os.getenv(f"{exchange_id.upper()}_API_SECRET")

        if api_key and api_secret:
            return {
                "apiKey": api_key,
                "secret": api_secret
            }
        return {}

    def mask_key(self, key: str) -> str:
        """
        Oculta parte da chave para exibição segura em logs.
        """
        if not key: return "N/A"
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
