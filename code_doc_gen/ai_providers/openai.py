from typing import Optional
from .base import AIProvider

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini'):
        super().__init__(api_key, model)
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {e}")

    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            response = self.client.chat.completions.create(
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
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.warning(f"OpenAI API call failed: {e}")
        
        return None
