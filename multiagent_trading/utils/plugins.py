import importlib
import inspect
from multiagent_trading.agents.base import BaseAgent

def load_agent_from_plugin(module_path, class_name, name, config, context, event_bus, logger):
    """
    Dynamically loads an agent class from a given module path.
    Example module_path: "plugins.custom_agent"
    """
    try:
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)

        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{class_name} must be a subclass of BaseAgent")

        return agent_class(name, config, context, event_bus, logger)
    except Exception as e:
        logger.error(f"Failed to load plugin {module_path}.{class_name}: {e}")
        return None

def discover_agents(package_name):
    """
    Discovers all BaseAgent subclasses in a given package.
    """
    discovered = []
    try:
        package = importlib.import_module(package_name)
        for name, obj in inspect.getmembers(package):
            if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                discovered.append(obj)
    except Exception as e:
        print(f"Discovery failed: {e}")
    return discovered
