from typing import Optional, List, Union
from .base import AIProvider

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class GroqProvider(AIProvider):
    def __init__(self, api_key: str, model: Optional[Union[str, List[str]]] = None):
        super().__init__(api_key, model)
        self.client = None
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = groq.Groq(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Groq client: {e}")
        
        # Default models if not provided
        if not self.model:
            self.model = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768']
        elif isinstance(self.model, str):
            self.model = [self.model]
        
        # At this point self.model is guaranteed to be a list of strings
        self.models: List[str] = self.model  # type: ignore

    def is_available(self) -> bool:
        return GROQ_AVAILABLE and bool(self.api_key) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available() or not self.models:
            return None

        # Try each model in order
        for model in self.models:
            try:
                # Ensure client is available
                assert self.client is not None
                
                self.logger.debug(f"Trying Groq model: {model}")
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
                
                if response.choices and len(response.choices) > 0:
                    self.logger.debug(f"Groq model {model} succeeded")
                    res_content = response.choices[0].message.content
                    return res_content.strip() if res_content else None
                
            except Exception as e:
                self.logger.warning(f"Groq model {model} failed: {e}")
                continue
        
        return None
