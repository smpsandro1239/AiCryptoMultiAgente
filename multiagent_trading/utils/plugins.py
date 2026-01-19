import importlib
import inspect
from multiagent_trading.agents.base import BaseAgent

class PluginManager:
    """
    Sistema de Plugins que permite o carregamento dinâmico de agentes customizados
    a partir de caminhos de módulos.
    """
    def __init__(self, logger):
        self.logger = logger
        self.plugins = {}

    def load_plugin(self, module_path: str):
        try:
            module = importlib.import_module(module_path)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    self.logger.info(f"Plugin carregado: {name} de {module_path}")
                    self.plugins[name] = obj
                    return obj
        except Exception as e:
            self.logger.error(f"Erro ao carregar plugin de {module_path}: {str(e)}")
            return None

    def get_plugin(self, name: str):
        return self.plugins.get(name)
