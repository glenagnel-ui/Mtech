from abc import ABC, abstractmethod
from src.core.llm_client import LLMClient
from src.core.config_loader import config_loader

class BaseAgent(ABC):
    def __init__(self):
        self.llm_client = LLMClient()
        self.system_config = config_loader.load_system_config()

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        The core operation method that all child agents must implement.
        """
        pass
