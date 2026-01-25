from typing import Optional, Union, List
from .base import AIProvider

try:
    from mistralai import Mistral  # type: ignore
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

class MistralProvider(AIProvider):
    def __init__(self, api_key: str, model: Union[str, List[str]] = 'mistral-small-latest'):
        super().__init__(api_key, model)
        self.client = None
        if MISTRAL_AVAILABLE and self.api_key:
            try:
                self.client = Mistral(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Mistral client: {e}")
        
        # Ensure models is a list
        if not self.model:
            self.models = ['mistral-small-latest']
        elif isinstance(self.model, str):
            self.models = [self.model]
        else:
            self.models = self.model

    def is_available(self) -> bool:
        return MISTRAL_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available() or self.client is None or not self.models:
            return None

        for model in self.models:
            try:
                # Use completion API
                response = self.client.chat.complete(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],  # type: ignore
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if response.choices:
                    choice = response.choices[0]
                    content = choice.message.content
                    if isinstance(content, str):
                        return content.strip()
                    # Handle other content types if necessary
                
            except Exception as e:
                self.logger.warning(f"Mistral model {model} failed: {e}")
                continue
        
        return None
