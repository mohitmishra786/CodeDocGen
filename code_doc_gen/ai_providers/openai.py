from typing import Optional, Union, List
from .base import AIProvider

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: Union[str, List[str]] = 'gpt-4o-mini'):
        super().__init__(api_key, model)
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        # Ensure models is a list
        if not self.model:
            self.models = ['gpt-4o-mini']
        elif isinstance(self.model, str):
            self.models = [self.model]
        else:
            self.models = self.model

    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available() or self.client is None or not self.models:
            return None

        for model in self.models:
            try:
                response = self.client.chat.completions.create(
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
                
                if response.choices:
                    content = response.choices[0].message.content
                    return content.strip() if content else None
                
            except Exception as e:
                self.logger.warning(f"OpenAI model {model} failed: {e}")
                continue
        
        return None
