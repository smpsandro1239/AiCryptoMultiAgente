import yaml
import os
from dotenv import load_dotenv

def load_config(path="config.yaml"):
    # Carregar variáveis de ambiente do ficheiro .env
    load_dotenv()

    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)

        # Substituir placeholders por variáveis de ambiente
        # Exemplo no yaml: telegram_token: ${TELEGRAM_TOKEN}
        return _replace_env_vars(config)
    except FileNotFoundError:
        return {}

def _replace_env_vars(config):
    if isinstance(config, dict):
        for k, v in config.items():
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                env_var = v[2:-1]
                config[k] = os.getenv(env_var, v)
            else:
                _replace_env_vars(v)
    elif isinstance(config, list):
        for i in range(len(config)):
            if isinstance(config[i], str) and config[i].startswith("${") and config[i].endswith("}"):
                env_var = config[i][2:-1]
                config[i] = os.getenv(env_var, config[i])
            else:
                _replace_env_vars(config[i])
    return config
