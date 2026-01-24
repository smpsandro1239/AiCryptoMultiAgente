import os
import json
import asyncio
from cryptography.fernet import Fernet

class SecurityManager:
    """
    Gere credenciais de exchange de forma segura, suportando criptografia AES.
    """
    _key = Fernet.generate_key() # Em produção, carregar de arquivo seguro ou KMS
    _cipher = Fernet(_key)

    @staticmethod
    def get_api_credentials(exchange_id: str):
        # Tenta carregar de variável de ambiente (prioridade)
        api_key = os.getenv(f"{exchange_id.upper()}_API_KEY")
        secret = os.getenv(f"{exchange_id.upper()}_API_SECRET")

        if api_key and secret:
            return {"apiKey": api_key, "secret": secret}

        # Caso contrário, tenta carregar do armazenamento cifrado local (mock)
        raise ValueError(f"Credenciais não encontradas para a exchange {exchange_id}.")

    @staticmethod
    def encrypt_data(data: str) -> str:
        """Cifra uma string utilizando AES."""
        return SecurityManager._cipher.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Decifra uma string cifrada."""
        return SecurityManager._cipher.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def store_credentials_locally(exchange_id: str, api_key: str, secret: str):
        # Simula a escrita cifrada num ficheiro local
        encrypted_key = SecurityManager.encrypt_data(api_key)
        encrypted_secret = SecurityManager.encrypt_data(secret)

        os.environ[f"{exchange_id.upper()}_API_KEY"] = api_key # Fallback para ambiente
        os.environ[f"{exchange_id.upper()}_API_SECRET"] = secret

    @staticmethod
    async def request_hardware_approval(transaction_data: dict) -> bool:
        """
        Simula a aprovação manual de uma transação através de uma Hardware Wallet (ex: Ledger, Trezor).
        Em produção, este método esperaria por um sinal físico do dispositivo USB/Bluetooth.
        """
        print(f"[SECURITY] Aguardando aprovação física no dispositivo para: {transaction_data.get('symbol')}")
        # Simulação de espera por aprovação (sempre retorna True neste mock)
        await asyncio.sleep(0.5)
        return True
