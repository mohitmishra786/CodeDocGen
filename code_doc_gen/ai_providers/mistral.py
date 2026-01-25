from typing import Optional
from .base import AIProvider

try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

class MistralProvider(AIProvider):
    def __init__(self, api_key: str, model: str = 'mistral-small-latest'):
        super().__init__(api_key, model)
        self.client = None
        if MISTRAL_AVAILABLE and self.api_key:
            try:
                self.client = MistralClient(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Mistral client: {e}")

    def is_available(self) -> bool:
        return MISTRAL_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            response = self.client.chat(
                model=self.model,
                messages=[ChatMessage(role="user", content=prompt)],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.warning(f"Mistral API call failed: {e}")
        
        return None
