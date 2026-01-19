import os

class SecurityManager:
    """
    Gere credenciais de exchange de forma segura, carregando-as de variáveis de ambiente.
    """
    @staticmethod
    def get_api_credentials(exchange_id: str):
        api_key = os.getenv(f"{exchange_id.upper()}_API_KEY")
        secret = os.getenv(f"{exchange_id.upper()}_API_SECRET")

        if not api_key or not secret:
            raise ValueError(f"Credenciais não encontradas para a exchange {exchange_id} nas variáveis de ambiente.")

        return {
            "apiKey": api_key,
            "secret": secret
        }

    @staticmethod
    def store_credentials_locally(exchange_id: str, api_key: str, secret: str):
        # Apenas para fins educacionais ou ambientes de teste, não recomendado para produção
        # Em produção, usaria um Secret Manager (AWS Secrets Manager, HashiCorp Vault, etc.)
        os.environ[f"{exchange_id.upper()}_API_KEY"] = api_key
        os.environ[f"{exchange_id.upper()}_API_SECRET"] = secret
