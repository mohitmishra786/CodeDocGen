from typing import Optional
from .base import AIProvider

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str = 'claude-3-haiku-20240307'):
        super().__init__(api_key, model)
        self.client = None
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Anthropic client: {e}")

    def is_available(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if response.content and len(response.content) > 0:
                return response.content[0].text.strip()
            
        except Exception as e:
            self.logger.warning(f"Anthropic API call failed: {e}")
        
        return None
