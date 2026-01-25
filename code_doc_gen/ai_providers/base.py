from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: str, model: Optional[Union[str, List[str]]] = None):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available (installed and configured)."""
        pass

    @abstractmethod
    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        """Generate documentation from a prompt."""
        pass
