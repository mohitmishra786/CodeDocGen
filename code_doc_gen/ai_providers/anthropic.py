from typing import Optional, Union, List
from .base import AIProvider

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: Union[str, List[str]] = 'claude-3-haiku-20240307'):
        super().__init__(api_key, model)
        self.client = None
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Anthropic client: {e}")
        
        # Ensure models is a list
        if not self.model:
            self.models = ['claude-3-haiku-20240307']
        elif isinstance(self.model, str):
            self.models = [self.model]
        else:
            self.models = self.model

    def is_available(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available() or self.client is None or not self.models:
            return None

        for model in self.models:
            try:
                response = self.client.messages.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if response.content:
                    for block in response.content:
                        if hasattr(block, 'text') and block.text.strip():
                            return block.text.strip()
                
            except Exception as e:
                self.logger.warning(f"Anthropic model {model} failed: {e}")
                continue
        
        return None
